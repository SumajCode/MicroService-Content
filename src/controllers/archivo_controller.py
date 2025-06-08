from flask import request, jsonify, send_file
from werkzeug.exceptions import BadRequest
from src.services.mongo_service import MongoService
from src.services.mega_service import MegaService
from src.services.educativo_service import EducativoService
from src.models.archivo_model import ArchivoModel, CarpetaUsuarioModel
from src.utils.file_utils import FileUtils
from src.config.settings import Config
import logging
import os
import tempfile
import zipfile
from io import BytesIO
from datetime import datetime
import uuid
from bson import ObjectId

logger = logging.getLogger(__name__)

class ArchivoController:
    def __init__(self):
        self.mongo_service = MongoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.educativo_service = EducativoService(Config.MONGO_URI)
        self.archivo_model = ArchivoModel()
        self.carpeta_model = CarpetaUsuarioModel()
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    # ==================== ARCHIVOS DE CONTENIDO ====================
    
    def subir_archivo_contenido(self):
        """1. Subir un archivo a una carpeta específica (Contenido Personal/Educativo)"""
        try:
            # Validar que se envió un archivo
            if 'archivo' not in request.files:
                return self._response_format("error", 400, "No se envió ningún archivo")
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                return self._response_format("error", 400, "No se seleccionó ningún archivo")
            
            # Obtener datos del formulario
            usuario_id = request.form.get('userId')
            carpeta = request.form.get('carpeta')  # "Contenido Personal" o "Contenido Educativo"
            
            if not usuario_id or not carpeta:
                return self._response_format("error", 400, "userId y carpeta son requeridos")
            
            # Validaciones
            if not FileUtils.archivo_permitido(archivo.filename):
                return self._response_format("error", 400, "Tipo de archivo no permitido")
            
            if not FileUtils.validar_carpeta(carpeta):
                return self._response_format("error", 400, "Carpeta inválida")
            
            # Obtener información del archivo
            archivo_info = FileUtils.obtener_info_archivo(archivo)
            
            # Verificar/crear carpetas del usuario
            self._verificar_carpetas_usuario(usuario_id)
            
            # Guardar archivo temporalmente
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                
                # Generar ruta en MEGA
                ruta_mega = FileUtils.generar_ruta_mega(usuario_id, carpeta)
                
                # Subir a MEGA
                resultado_mega = self.mega_service.subir_archivo(
                    temp_path, 
                    ruta_mega, 
                    archivo_info['nombre']
                )
                
                if not resultado_mega:
                    return self._response_format("error", 500, "Error al subir archivo a MEGA")
                
                # Actualizar información del archivo
                archivo_info.update({
                    "link": resultado_mega['link'],
                    "ruta": ruta_mega + archivo_info['nombre'],
                    "mega_node_id": resultado_mega['node_id']
                })
                
                # Crear documento para MongoDB
                documento = ArchivoModel.crear_documento_archivo(
                    usuario_id,
                    carpeta,
                    archivo_info
                )
                
                # Guardar en MongoDB
                archivo_id = self.mongo_service.insertar_archivo(documento)
                
                return self._response_format("success", 201, "Archivo subido exitosamente", {
                    "userId": usuario_id,
                    "file": {
                        "id": archivo_id,
                        "secureName": archivo_info['nombre'],
                        "originalName": archivo.filename,
                        "contentType": archivo_info['mime'],
                        "size": archivo_info['peso_bytes'],
                        "link": resultado_mega['link']
                    }
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivo de contenido: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_multiples_archivos_contenido(self):
        """2. Subir múltiples archivos a una carpeta específica"""
        try:
            # Validar que se enviaron archivos
            if 'archivos' not in request.files:
                return self._response_format("error", 400, "No se enviaron archivos")
            
            archivos = request.files.getlist('archivos')
            if not archivos or all(archivo.filename == '' for archivo in archivos):
                return self._response_format("error", 400, "No se seleccionaron archivos")
            
            # Obtener datos del formulario
            usuario_id = request.form.get('userId')
            carpeta = request.form.get('carpeta')
            
            if not usuario_id or not carpeta:
                return self._response_format("error", 400, "userId y carpeta son requeridos")
            
            if not FileUtils.validar_carpeta(carpeta):
                return self._response_format("error", 400, "Carpeta inválida")
            
            # Verificar/crear carpetas del usuario
            self._verificar_carpetas_usuario(usuario_id)
            
            archivos_subidos = []
            errores = []
            
            for archivo in archivos:
                try:
                    if archivo.filename == '':
                        continue
                        
                    if not FileUtils.archivo_permitido(archivo.filename):
                        errores.append(f"Archivo {archivo.filename}: tipo no permitido")
                        continue
                    
                    # Obtener información del archivo
                    archivo_info = FileUtils.obtener_info_archivo(archivo)
                    
                    # Guardar archivo temporalmente
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                        
                        # Generar ruta en MEGA
                        ruta_mega = FileUtils.generar_ruta_mega(usuario_id, carpeta)
                        
                        # Subir a MEGA
                        resultado_mega = self.mega_service.subir_archivo(
                            temp_path, 
                            ruta_mega, 
                            archivo_info['nombre']
                        )
                        
                        if not resultado_mega:
                            errores.append(f"Error al subir {archivo.filename} a MEGA")
                            continue
                        
                        # Actualizar información del archivo
                        archivo_info.update({
                            "link": resultado_mega['link'],
                            "ruta": ruta_mega + archivo_info['nombre'],
                            "mega_node_id": resultado_mega['node_id']
                        })
                        
                        # Crear documento para MongoDB
                        documento = ArchivoModel.crear_documento_archivo(
                            usuario_id,
                            carpeta,
                            archivo_info
                        )
                        
                        # Guardar en MongoDB
                        archivo_id = self.mongo_service.insertar_archivo(documento)
                        
                        archivos_subidos.append({
                            "id": archivo_id,
                            "secureName": archivo_info['nombre'],
                            "originalName": archivo.filename,
                            "contentType": archivo_info['mime'],
                            "size": archivo_info['peso_bytes'],
                            "link": resultado_mega['link']
                        })
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
            if archivos_subidos:
                message = f"Se subieron {len(archivos_subidos)} archivos exitosamente"
                if errores:
                    message += f". {len(errores)} archivos fallaron"
                
                return self._response_format("success", 201, message, {
                    "userId": usuario_id,
                    "files": archivos_subidos,
                    "errors": errores if errores else None
                })
            else:
                return self._response_format("error", 400, "No se pudo subir ningún archivo", {
                    "errors": errores
                })
                
        except Exception as e:
            logger.error(f"Error al subir múltiples archivos de contenido: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def obtener_info_archivo_contenido(self):
        """3. Obtener información de un archivo de contenido"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            archivo_id = data.get('fileId')
            usuario_id = data.get('userId')
            
            if not archivo_id or not usuario_id:
                return self._response_format("error", 400, "fileId y userId son requeridos")
            
            # Obtener archivo de la base de datos
            archivo = self.mongo_service.obtener_archivo_por_id(archivo_id)
            if not archivo:
                return self._response_format("error", 404, "Archivo no encontrado")
            
            # Verificar que el archivo pertenece al usuario
            if archivo['usuario_id'] != usuario_id:
                return self._response_format("error", 403, "No tienes permisos para acceder a este archivo")
            
            return self._response_format("success", 200, "Información del archivo obtenida", {
                "userId": usuario_id,
                "file": {
                    "id": str(archivo['_id']),
                    "secureName": archivo['archivo']['nombre'],
                    "originalName": archivo['archivo']['nombre'],
                    "contentType": archivo['archivo']['tipo'],
                    "size": archivo['archivo']['peso'],
                    "link": archivo['archivo']['link']
                }
            })
            
        except Exception as e:
            logger.error(f"Error al obtener información del archivo de contenido: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def listar_archivos_contenido(self):
        """4. Listar archivos de contenido por carpeta"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            usuario_id = data.get('userId')
            carpeta = data.get('carpeta')
            
            if not usuario_id or not carpeta:
                return self._response_format("error", 400, "userId y carpeta son requeridos")
            
            if not FileUtils.validar_carpeta(carpeta):
                return self._response_format("error", 400, "Carpeta inválida")
            
            # Obtener archivos del usuario en la carpeta específica
            archivos = self.mongo_service.obtener_archivos_usuario_carpeta(usuario_id, carpeta)
            
            # Filtrar archivos activos
            archivos_activos = [
                {
                    "id": str(archivo['_id']),
                    "secureName": archivo['archivo']['nombre'],
                    "originalName": archivo['archivo']['nombre'],
                    "contentType": archivo['archivo']['tipo'],
                    "size": archivo['archivo']['peso'],
                    "link": archivo['archivo']['link']
                }
                for archivo in archivos 
                if archivo.get('estado') == 'activo'
            ]
            
            return self._response_format("success", 200, f"Archivos de la carpeta {carpeta} obtenidos", {
                "userId": usuario_id,
                "carpeta": carpeta,
                "totalFiles": len(archivos_activos),
                "files": archivos_activos
            })
            
        except Exception as e:
            logger.error(f"Error al listar archivos de contenido: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def descargar_archivo_contenido(self):
        """5. Descargar un archivo de contenido"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            archivo_id = data.get('fileId')
            usuario_id = data.get('userId')
            
            if not archivo_id or not usuario_id:
                return self._response_format("error", 400, "fileId y userId son requeridos")
            
            # Obtener archivo de la base de datos
            archivo = self.mongo_service.obtener_archivo_por_id(archivo_id)
            if not archivo:
                return self._response_format("error", 404, "Archivo no encontrado")
            
            # Verificar que el archivo pertenece al usuario
            if archivo['usuario_id'] != usuario_id:
                return self._response_format("error", 403, "No tienes permisos para acceder a este archivo")
            
            # Descargar archivo de MEGA
            archivo_descargado = self.mega_service.descargar_archivo(archivo['archivo']['mega_node_id'])
            
            if not archivo_descargado:
                return self._response_format("error", 500, "Error al descargar archivo de MEGA")
            
            return send_file(
                archivo_descargado,
                as_attachment=True,
                download_name=archivo['archivo']['nombre'],
                mimetype=archivo['archivo']['tipo']
            )
            
        except Exception as e:
            logger.error(f"Error al descargar archivo de contenido: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_archivo_contenido(self):
        """6. Eliminar un archivo de contenido"""
        try:
            data = request.get_json()
            logger.info("Solicitud recibida para eliminar archivo de contenido.")
            logger.debug(f"Payload recibido: {data}")

            if not data:
                logger.warning("No se recibieron datos JSON en la solicitud.")
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            archivo_id = data.get('fileId')
            usuario_id = data.get('userId')
            
            if not archivo_id or not usuario_id:
                logger.warning("Faltan 'fileId' o 'userId' en los datos recibidos.")
                return self._response_format("error", 400, "fileId y userId son requeridos")
            
            # Obtener archivo de la base de datos
            logger.info(f"Buscando archivo con ID {archivo_id} en MongoDB.")
            archivo = self.mongo_service.obtener_archivo_por_id(archivo_id)
            if not archivo:
                logger.error(f"Archivo con ID {archivo_id} no encontrado.")
                return self._response_format("error", 404, "Archivo no encontrado")
            
            # Verificar que el archivo pertenece al usuario
            logger.info(f"Verificando propiedad del archivo para el usuario {usuario_id}.")
            if archivo['usuario_id'] != usuario_id:
                logger.warning(f"Usuario {usuario_id} no tiene permiso para eliminar el archivo {archivo_id}.")
                return self._response_format("error", 403, "No tienes permisos para eliminar este archivo")
            
            # Extraer node_id real
            logger.debug("Extrayendo node_id de MEGA.")
            mega_node_data = archivo['archivo'].get('mega_node_id')
            logger.debug(f"mega_node_id obtenido: {mega_node_data}")

            # Si es string, usarlo directamente
            if isinstance(mega_node_data, str):
                node_id = mega_node_data
                logger.debug("mega_node_id es un string válido.")
            # Si es dict con estructura tipo {'f': [{'h': ...}]}
            elif isinstance(mega_node_data, dict):
                node_id = mega_node_data.get('f', [{}])[0].get('h')
                logger.debug(f"mega_node_id extraído desde estructura dict: {node_id}")
            else:
                node_id = None
                logger.warning("mega_node_id no tiene un formato válido.")

            if node_id:
                logger.info(f"Intentando eliminar archivo de MEGA con node_id: {node_id}")
            else:
                logger.error("No se pudo obtener un node_id válido.")

            # Validar que tengamos un node_id y eliminar
            if node_id and self.mega_service.eliminar_archivo(node_id):
                logger.info(f"Archivo eliminado de MEGA exitosamente: {node_id}")
                logger.info(f"Intentando eliminar referencia en MongoDB: {archivo_id}")
                if self.mongo_service.ealiminar_archivo(archivo_id):
                    logger.info(f"Archivo eliminado de MongoDB exitosamente: {archivo_id}")
                    return self._response_format("success", 200, "Archivo eliminado exitosamente", {
                        "userId": usuario_id,
                        "fileId": archivo_id
                    })
                else:
                    logger.error("Falló la eliminación del archivo en MongoDB.")
                    return self._response_format("error", 500, "Error al actualizar estado en base de datos")
            else:
                logger.error("Falló la eliminación del archivo en MEGA.")
                return self._response_format("error", 500, "Error al eliminar archivo de MEGA")
                
        except Exception as e:
            logger.exception(f"Error al eliminar archivo de contenido: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    # ==================== ARCHIVOS EDUCATIVOS ====================
    
    def subir_archivo_publicacion(self):
        """7. Subir archivos para publicación"""
        try:
            # Validar que se enviaron archivos
            if 'archivos' not in request.files:
                return self._response_format("error", 400, "No se enviaron archivos")
            
            archivos = request.files.getlist('archivos')
            if not archivos or all(archivo.filename == '' for archivo in archivos):
                return self._response_format("error", 400, "No se seleccionaron archivos")
            
            # Obtener datos del formulario
            publicacion_id = request.form.get('publicacion_id')
            autor_id = request.form.get('autor_id')
            
            if not publicacion_id or not autor_id:
                return self._response_format("error", 400, "publicacion_id y autor_id son requeridos")
            
            archivos_subidos = []
            errores = []
            
            # Crear carpeta en MEGA si no existe
            ruta_mega = f"/Archivo/publicacion/{publicacion_id}/"
            
            for archivo in archivos:
                try:
                    if archivo.filename == '':
                        continue
                        
                    # Validaciones
                    if not FileUtils.archivo_permitido(archivo.filename):
                        errores.append(f"Archivo {archivo.filename}: tipo no permitido")
                        continue
                    
                    # Obtener información del archivo
                    archivo_info = FileUtils.obtener_info_archivo(archivo)
                    
                    # Generar nombre único
                    nombre_unico = f"{uuid.uuid4()}_{archivo_info['nombre']}"
                    
                    # Guardar archivo temporalmente
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                        
                        # Subir a MEGA
                        resultado_mega = self.mega_service.subir_archivo(
                            temp_path, 
                            ruta_mega, 
                            nombre_unico
                        )
                        
                        if not resultado_mega:
                            errores.append(f"Error al subir {archivo.filename} a MEGA")
                            continue
                        
                        # Crear documento de archivo educativo
                        documento_archivo = {
                            "usuario_id": autor_id,
                            "tipo_usuario": "docente",
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes'],
                            "modulo_origen": "publicacion",
                            "referencia_id": publicacion_id,
                            "mega_node_id": resultado_mega['node_id'],
                            "fecha_subida": datetime.utcnow()
                        }
                        
                        # Guardar en MongoDB (colección archivos)
                        archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
                        
                        archivo_info_respuesta = {
                            "archivo_id": archivo_id,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes']
                        }
                        
                        archivos_subidos.append(archivo_info_respuesta)
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
            # Actualizar el campo archivos en la publicación
            if archivos_subidos:
                try:
                    # Obtener publicación actual
                    publicacion = self.educativo_service.publicaciones_collection.find_one({"_id": ObjectId(publicacion_id)})
                    if publicacion:
                        archivos_actuales = publicacion.get('archivos', [])
                        archivos_actuales.extend(archivos_subidos)
                        
                        # Actualizar publicación con nuevos archivos
                        self.educativo_service.actualizar_publicacion(publicacion_id, {
                            'archivos': archivos_actuales
                        })
                        logger.info(f"Campo archivos actualizado en publicación {publicacion_id}")
                    else:
                        logger.error(f"Publicación {publicacion_id} no encontrada")
                except Exception as e:
                    logger.error(f"Error al actualizar campo archivos en publicación: {e}")
            
            if archivos_subidos:
                message = f"Se subieron {len(archivos_subidos)} archivos exitosamente"
                if errores:
                    message += f". {len(errores)} archivos fallaron"
                
                return self._response_format("success", 201, message, {
                    "publicacion_id": publicacion_id,
                    "autor_id": autor_id,
                    "archivos": archivos_subidos,
                    "errores": errores if errores else None
                })
            else:
                return self._response_format("error", 400, "No se pudo subir ningún archivo", {
                    "errores": errores
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivos de publicación: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_tarea(self):
        """8. Subir archivos para tarea"""
        try:
            # Validar que se enviaron archivos
            if 'archivos' not in request.files:
                return self._response_format("error", 400, "No se enviaron archivos")
            
            archivos = request.files.getlist('archivos')
            if not archivos or all(archivo.filename == '' for archivo in archivos):
                return self._response_format("error", 400, "No se seleccionaron archivos")
            
            # Obtener datos del formulario
            tarea_id = request.form.get('tarea_id')
            autor_id = request.form.get('autor_id')
            
            if not tarea_id or not autor_id:
                return self._response_format("error", 400, "tarea_id y autor_id son requeridos")
            
            archivos_subidos = []
            errores = []
            
            # Crear carpeta en MEGA si no existe
            ruta_mega = f"/Archivo/tarea/{tarea_id}/"
            
            for archivo in archivos:
                try:
                    if archivo.filename == '':
                        continue
                        
                    # Validaciones
                    if not FileUtils.archivo_permitido(archivo.filename):
                        errores.append(f"Archivo {archivo.filename}: tipo no permitido")
                        continue
                    
                    # Obtener información del archivo
                    archivo_info = FileUtils.obtener_info_archivo(archivo)
                    
                    # Generar nombre único
                    nombre_unico = f"{uuid.uuid4()}_{archivo_info['nombre']}"
                    
                    # Guardar archivo temporalmente
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                        
                        # Subir a MEGA
                        resultado_mega = self.mega_service.subir_archivo(
                            temp_path, 
                            ruta_mega, 
                            nombre_unico
                        )
                        
                        if not resultado_mega:
                            errores.append(f"Error al subir {archivo.filename} a MEGA")
                            continue
                        
                        # Crear documento de archivo educativo
                        documento_archivo = {
                            "usuario_id": autor_id,
                            "tipo_usuario": "docente",
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes'],
                            "modulo_origen": "tarea",
                            "referencia_id": tarea_id,
                            "mega_node_id": resultado_mega['node_id'],
                            "fecha_subida": datetime.utcnow()
                        }
                        
                        # Guardar en MongoDB (colección archivos)
                        archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
                        
                        archivo_info_respuesta = {
                            "archivo_id": archivo_id,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes']
                        }
                        
                        archivos_subidos.append(archivo_info_respuesta)
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
            # Actualizar el campo archivos en la tarea
            if archivos_subidos:
                try:
                    # Obtener tarea actual
                    tarea = self.educativo_service.tareas_collection.find_one({"_id": ObjectId(tarea_id)})
                    if tarea:
                        archivos_actuales = tarea.get('archivos', [])
                        archivos_actuales.extend(archivos_subidos)
                        
                        # Actualizar tarea con nuevos archivos
                        self.educativo_service.actualizar_tarea(tarea_id, {
                            'archivos': archivos_actuales
                        })
                        logger.info(f"Campo archivos actualizado en tarea {tarea_id}")
                    else:
                        logger.error(f"Tarea {tarea_id} no encontrada")
                except Exception as e:
                    logger.error(f"Error al actualizar campo archivos en tarea: {e}")
            
            if archivos_subidos:
                message = f"Se subieron {len(archivos_subidos)} archivos exitosamente"
                if errores:
                    message += f". {len(errores)} archivos fallaron"
                
                return self._response_format("success", 201, message, {
                    "tarea_id": tarea_id,
                    "autor_id": autor_id,
                    "archivos": archivos_subidos,
                    "errores": errores if errores else None
                })
            else:
                return self._response_format("error", 400, "No se pudo subir ningún archivo", {
                    "errores": errores
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivos de tarea: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_entrega(self):
        """9. Subir archivos para entrega"""
        try:
            # Validar que se enviaron archivos
            if 'archivos' not in request.files:
                return self._response_format("error", 400, "No se enviaron archivos")
            
            archivos = request.files.getlist('archivos')
            if not archivos or all(archivo.filename == '' for archivo in archivos):
                return self._response_format("error", 400, "No se seleccionaron archivos")
            
            # Obtener datos del formulario
            id_tarea = request.form.get('id_tarea')
            id_estudiante = request.form.get('id_estudiante')
            
            if not id_tarea or not id_estudiante:
                return self._response_format("error", 400, "id_tarea e id_estudiante son requeridos")
            
            archivos_subidos = []
            errores = []
            
            # Crear carpeta en MEGA si no existe
            ruta_mega = f"/Archivo/entrega/{id_tarea}/{id_estudiante}/"
            
            for archivo in archivos:
                try:
                    if archivo.filename == '':
                        continue
                        
                    # Validaciones
                    if not FileUtils.archivo_permitido(archivo.filename):
                        errores.append(f"Archivo {archivo.filename}: tipo no permitido")
                        continue
                    
                    # Obtener información del archivo
                    archivo_info = FileUtils.obtener_info_archivo(archivo)
                    
                    # Generar nombre único
                    nombre_unico = f"{uuid.uuid4()}_{archivo_info['nombre']}"
                    
                    # Guardar archivo temporalmente
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                        
                        # Subir a MEGA
                        resultado_mega = self.mega_service.subir_archivo(
                            temp_path, 
                            ruta_mega, 
                            nombre_unico
                        )
                        
                        if not resultado_mega:
                            errores.append(f"Error al subir {archivo.filename} a MEGA")
                            continue
                        
                        # Crear documento de archivo educativo
                        documento_archivo = {
                            "usuario_id": id_estudiante,
                            "tipo_usuario": "estudiante",
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes'],
                            "modulo_origen": "entrega",
                            "referencia_id": id_tarea,
                            "mega_node_id": resultado_mega['node_id'],
                            "fecha_subida": datetime.utcnow()
                        }
                        
                        # Guardar en MongoDB (colección archivos)
                        archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
                        
                        archivo_info_respuesta = {
                            "archivo_id": archivo_id,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes']
                        }
                        
                        archivos_subidos.append(archivo_info_respuesta)
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
            # Actualizar el campo archivos en la entrega
            if archivos_subidos:
                try:
                    # Buscar entrega existente
                    entrega = self.educativo_service.obtener_entrega_estudiante(id_tarea, id_estudiante)
                    if entrega:
                        archivos_actuales = entrega.get('archivos', [])
                        archivos_actuales.extend(archivos_subidos)
                        
                        # Actualizar entrega con nuevos archivos
                        self.educativo_service.actualizar_entrega(str(entrega['_id']), {
                            'archivos': archivos_actuales
                        })
                        logger.info(f"Campo archivos actualizado en entrega {entrega['_id']}")
                    else:
                        logger.warning(f"No se encontró entrega para tarea {id_tarea} y estudiante {id_estudiante}")
                except Exception as e:
                    logger.error(f"Error al actualizar campo archivos en entrega: {e}")
            
            if archivos_subidos:
                message = f"Se subieron {len(archivos_subidos)} archivos exitosamente"
                if errores:
                    message += f". {len(errores)} archivos fallaron"
                
                return self._response_format("success", 201, message, {
                    "id_tarea": id_tarea,
                    "id_estudiante": id_estudiante,
                    "archivos": archivos_subidos,
                    "errores": errores if errores else None
                })
            else:
                return self._response_format("error", 400, "No se pudo subir ningún archivo", {
                    "errores": errores
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivos de entrega: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_anuncio(self):
        """10. Subir archivos para anuncio"""
        try:
            # Validar que se enviaron archivos
            if 'archivos' not in request.files:
                return self._response_format("error", 400, "No se enviaron archivos")
            
            archivos = request.files.getlist('archivos')
            if not archivos or all(archivo.filename == '' for archivo in archivos):
                return self._response_format("error", 400, "No se seleccionaron archivos")
            
            # Obtener datos del formulario
            anuncio_id = request.form.get('anuncio_id')
            autor_id = request.form.get('autor_id')
            tipo_usuario = request.form.get('tipo_usuario', 'docente')
            
            if not anuncio_id or not autor_id:
                return self._response_format("error", 400, "anuncio_id y autor_id son requeridos")
            
            archivos_subidos = []
            errores = []
            
            # Crear carpeta en MEGA si no existe
            ruta_mega = f"/Archivo/anuncio/{anuncio_id}/"
            
            for archivo in archivos:
                try:
                    if archivo.filename == '':
                        continue
                        
                    # Validaciones
                    if not FileUtils.archivo_permitido(archivo.filename):
                        errores.append(f"Archivo {archivo.filename}: tipo no permitido")
                        continue
                    
                    # Obtener información del archivo
                    archivo_info = FileUtils.obtener_info_archivo(archivo)
                    
                    # Generar nombre único
                    nombre_unico = f"{uuid.uuid4()}_{archivo_info['nombre']}"
                    
                    # Guardar archivo temporalmente
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                        
                        # Subir a MEGA
                        resultado_mega = self.mega_service.subir_archivo(
                            temp_path, 
                            ruta_mega, 
                            nombre_unico
                        )
                        
                        if not resultado_mega:
                            errores.append(f"Error al subir {archivo.filename} a MEGA")
                            continue
                        
                        # Crear documento de archivo educativo
                        documento_archivo = {
                            "usuario_id": autor_id,
                            "tipo_usuario": tipo_usuario,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes'],
                            "modulo_origen": "anuncio",
                            "referencia_id": anuncio_id,
                            "mega_node_id": resultado_mega['node_id'],
                            "fecha_subida": datetime.utcnow()
                        }
                        
                        # Guardar en MongoDB (colección archivos)
                        archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
                        
                        archivo_info_respuesta = {
                            "archivo_id": archivo_id,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes']
                        }
                        
                        archivos_subidos.append(archivo_info_respuesta)
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
            # Actualizar el campo archivos en el anuncio
            if archivos_subidos:
                try:
                    # Obtener anuncio actual
                    anuncio = self.educativo_service.anuncios_collection.find_one({"_id": ObjectId(anuncio_id)})
                    if anuncio:
                        archivos_actuales = anuncio.get('archivos', [])
                        archivos_actuales.extend(archivos_subidos)
                        
                        # Actualizar anuncio con nuevos archivos
                        self.educativo_service.actualizar_anuncio(anuncio_id, {
                            'archivos': archivos_actuales
                        })
                        logger.info(f"Campo archivos actualizado en anuncio {anuncio_id}")
                    else:
                        logger.error(f"Anuncio {anuncio_id} no encontrado")
                except Exception as e:
                    logger.error(f"Error al actualizar campo archivos en anuncio: {e}")
            
            if archivos_subidos:
                message = f"Se subieron {len(archivos_subidos)} archivos exitosamente"
                if errores:
                    message += f". {len(errores)} archivos fallaron"
                
                return self._response_format("success", 201, message, {
                    "anuncio_id": anuncio_id,
                    "autor_id": autor_id,
                    "archivos": archivos_subidos,
                    "errores": errores if errores else None
                })
            else:
                return self._response_format("error", 400, "No se pudo subir ningún archivo", {
                    "errores": errores
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivos de anuncio: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def obtener_archivos_modulo(self):
        """11. Obtener archivos por módulo educativo"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            modulo_origen = data.get('modulo_origen')
            referencia_id = data.get('referencia_id')
            
            if not modulo_origen or not referencia_id:
                return self._response_format("error", 400, "modulo_origen y referencia_id son requeridos")
            
            archivos = self.educativo_service.obtener_archivos_por_modulo(modulo_origen, referencia_id)
            
            # Formatear respuesta
            archivos_formateados = []
            for archivo in archivos:
                archivos_formateados.append({
                    "id": str(archivo['_id']),
                    "usuario_id": archivo['usuario_id'],
                    "tipo_usuario": archivo['tipo_usuario'],
                    "nombre_original": archivo['nombre_original'],
                    "nombre_almacenado": archivo['nombre_almacenado'],
                    "url": archivo['url'],
                    "tipo": archivo['tipo'],
                    "peso": archivo['peso'],
                    "modulo_origen": archivo['modulo_origen'],
                    "referencia_id": archivo['referencia_id'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            return self._response_format("success", 200, "Archivos obtenidos exitosamente", {
                "modulo_origen": modulo_origen,
                "referencia_id": referencia_id,
                "total_archivos": len(archivos_formateados),
                "archivos": archivos_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al obtener archivos por módulo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def obtener_archivos_usuario_educativo(self):
        """12. Obtener archivos educativos por usuario"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            usuario_id = data.get('usuario_id')
            tipo_usuario = data.get('tipo_usuario')
            
            if not usuario_id or not tipo_usuario:
                return self._response_format("error", 400, "usuario_id y tipo_usuario son requeridos")
            
            archivos = self.educativo_service.obtener_archivos_por_usuario(usuario_id, tipo_usuario)
            
            # Formatear respuesta
            archivos_formateados = []
            for archivo in archivos:
                archivos_formateados.append({
                    "id": str(archivo['_id']),
                    "usuario_id": archivo['usuario_id'],
                    "tipo_usuario": archivo['tipo_usuario'],
                    "nombre_original": archivo['nombre_original'],
                    "nombre_almacenado": archivo['nombre_almacenado'],
                    "url": archivo['url'],
                    "tipo": archivo['tipo'],
                    "peso": archivo['peso'],
                    "modulo_origen": archivo['modulo_origen'],
                    "referencia_id": archivo['referencia_id'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            return self._response_format("success", 200, "Archivos obtenidos exitosamente", {
                "usuario_id": usuario_id,
                "tipo_usuario": tipo_usuario,
                "total_archivos": len(archivos_formateados),
                "archivos": archivos_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al obtener archivos por usuario educativo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_archivo_educativo(self):
        """13. Eliminar archivo educativo"""
        try:
            logger.info("Iniciando eliminación de archivo educativo")

            data = request.get_json()
            logger.debug(f"Datos recibidos: {data}")

            if not data:
                logger.warning("No se proporcionaron datos JSON")
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            archivo_id = data.get('_id')
            logger.info(f"Buscando archivo con ID: {archivo_id}")

            if not archivo_id:
                logger.warning("No se proporcionó _id del archivo")
                return self._response_format("error", 400, "_id es requerido")
            
            logger.info(f"Archivo encontrado: {archivo}")

            # Obtener archivo de la base de datos
            archivo = self.educativo_service.archivos_collection.find_one({"_id": ObjectId(archivo_id)})
            if not archivo:
                return self._response_format("error", 404, "Archivo no encontrado")
            
            # Eliminar de MEGA si tiene mega_node_id
            mega_node_data = archivo.get('mega_node_id')
            node_id = None
            if isinstance(mega_node_data, str):
                node_id = mega_node_data
            elif isinstance(mega_node_data, dict):
                node_id = mega_node_data.get('f', [{}])[0].get('h')

            if node_id:
                logger.info(f"Intentando eliminar archivo en MEGA con node_id: {node_id}")
                mega_eliminado = self.mega_service.eliminar_archivo(node_id)
                if mega_eliminado:
                    logger.info("Archivo eliminado de MEGA correctamente")
                else:
                    logger.warning(f"No se pudo eliminar archivo de MEGA con node_id: {node_id}")
            else:
                logger.warning("mega_node_id no válido o ausente, omitiendo eliminación de MEGA")
            
            # Eliminar de MongoDB
            logger.info("Eliminando archivo de la base de datos educativa")
            eliminado = self.educativo_service.eliminar_archivo_educativo(archivo_id)
            
            if eliminado:
                logger.info("Archivo eliminado de MongoDB correctamente")
                # Actualizar el campo archivos en la colección correspondiente
                try:
                    modulo = archivo.get('modulo_origen')
                    referencia_id = archivo.get('referencia_id')
                    logger.debug(f"Modulo origen: {modulo}, referencia ID: {referencia_id}")
                    
                    if modulo and referencia_id:
                        # Obtener documento del módulo
                        logger.info(f"Actualizando documento del módulo {modulo} para referencia {referencia_id}")
                        if modulo == 'publicacion':
                            doc = self.educativo_service.publicaciones_collection.find_one({"_id": ObjectId(referencia_id)})
                            if doc:
                                archivos_actuales = [a for a in doc.get('archivos', []) if a.get('archivo_id') != archivo_id]
                                self.educativo_service.actualizar_publicacion(referencia_id, {'archivos': archivos_actuales})
                                logger.info("Publicación actualizada correctamente")
                        elif modulo == 'tarea':
                            doc = self.educativo_service.tareas_collection.find_one({"_id": ObjectId(referencia_id)})
                            if doc:
                                archivos_actuales = [a for a in doc.get('archivos', []) if a.get('archivo_id') != archivo_id]
                                self.educativo_service.actualizar_tarea(referencia_id, {'archivos': archivos_actuales})
                                logger.info("Tarea actualizada correctamente")
                        elif modulo == 'anuncio':
                            doc = self.educativo_service.anuncios_collection.find_one({"_id": ObjectId(referencia_id)})
                            if doc:
                                archivos_actuales = [a for a in doc.get('archivos', []) if a.get('archivo_id') != archivo_id]
                                self.educativo_service.actualizar_anuncio(referencia_id, {'archivos': archivos_actuales})
                                logger.info("Anuncio actualizado correctamente")
                        elif modulo == 'entrega':
                            entrega = self.educativo_service.obtener_entrega_estudiante(referencia_id, archivo['usuario_id'])
                            if entrega:
                                archivos_actuales = [a for a in entrega.get('archivos', []) if a.get('archivo_id') != archivo_id]
                                self.educativo_service.actualizar_entrega(str(entrega['_id']), {'archivos': archivos_actuales})
                                logger.info("Entrega actualizada correctamente")
                except Exception as e:
                    logger.error(f"Error al actualizar campo archivos después de eliminar: {e}")
                
                return self._response_format("success", 200, "Archivo eliminado exitosamente", {
                    "archivo_id": archivo_id
                })
            else:
                logger.warning(f"No se pudo eliminar el archivo con ID {archivo_id} en la base de datos")
                return self._response_format("error", 404, "Archivo no encontrado o no se pudo eliminar")
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo educativo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    # ==================== ENDPOINTS GENERALES ====================
    
    def listar_todos_archivos(self):
        """14. Listar todos los archivos (educativos y contenido)"""
        try:
            # Obtener archivos de contenido
            archivos_contenido = list(self.mongo_service.archivos_collection.find({"estado": "activo"}).sort("fecha_subida", -1))
            
            # Obtener archivos educativos
            archivos_educativos = list(self.educativo_service.archivos_collection.find().sort("fecha_subida", -1))
            
            # Formatear archivos de contenido
            contenido_formateado = []
            for archivo in archivos_contenido:
                contenido_formateado.append({
                    "id": str(archivo['_id']),
                    "tipo_archivo": "contenido",
                    "usuario_id": archivo['usuario_id'],
                    "carpeta": archivo['carpeta'],
                    "nombre": archivo['archivo']['nombre'],
                    "tipo": archivo['archivo']['tipo'],
                    "peso": archivo['archivo']['peso'],
                    "link": archivo['archivo']['link'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            # Formatear archivos educativos
            educativo_formateado = []
            for archivo in archivos_educativos:
                educativo_formateado.append({
                    "id": str(archivo['_id']),
                    "tipo_archivo": "educativo",
                    "usuario_id": archivo['usuario_id'],
                    "tipo_usuario": archivo['tipo_usuario'],
                    "nombre_original": archivo['nombre_original'],
                    "nombre_almacenado": archivo['nombre_almacenado'],
                    "url": archivo['url'],
                    "tipo": archivo['tipo'],
                    "peso": archivo['peso'],
                    "modulo_origen": archivo['modulo_origen'],
                    "referencia_id": archivo['referencia_id'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            return self._response_format("success", 200, "Todos los archivos obtenidos exitosamente", {
                "total_archivos": len(contenido_formateado) + len(educativo_formateado),
                "archivos_contenido": {
                    "total": len(contenido_formateado),
                    "archivos": contenido_formateado
                },
                "archivos_educativos": {
                    "total": len(educativo_formateado),
                    "archivos": educativo_formateado
                }
            })
            
        except Exception as e:
            logger.error(f"Error al listar todos los archivos: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def buscar_archivos(self):
        """15. Buscar archivos por criterios"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            termino_busqueda = data.get('termino')
            usuario_id = data.get('usuario_id')
            tipo_archivo = data.get('tipo_archivo')  # 'contenido', 'educativo', 'todos'
            
            if not termino_busqueda:
                return self._response_format("error", 400, "termino de búsqueda es requerido")
            
            resultados = []
            
            # Buscar en archivos de contenido
            if tipo_archivo in ['contenido', 'todos']:
                if usuario_id:
                    archivos_contenido = self.mongo_service.buscar_archivos(usuario_id, termino_busqueda)
                else:
                    # Buscar en todos los archivos de contenido
                    filtro = {
                        "estado": "activo",
                        "archivo.nombre": {"$regex": termino_busqueda, "$options": "i"}
                    }
                    archivos_contenido = list(self.mongo_service.archivos_collection.find(filtro))
                
                for archivo in archivos_contenido:
                    resultados.append({
                        "id": str(archivo['_id']),
                        "tipo_archivo": "contenido",
                        "usuario_id": archivo['usuario_id'],
                        "carpeta": archivo['carpeta'],
                        "nombre": archivo['archivo']['nombre'],
                        "tipo": archivo['archivo']['tipo'],
                        "peso": archivo['archivo']['peso'],
                        "link": archivo['archivo']['link'],
                        "fecha_subida": archivo['fecha_subida'].isoformat()
                    })
            
            # Buscar en archivos educativos
            if tipo_archivo in ['educativo', 'todos']:
                filtro_educativo = {
                    "nombre_original": {"$regex": termino_busqueda, "$options": "i"}
                }
                if usuario_id:
                    filtro_educativo["usuario_id"] = usuario_id
                
                archivos_educativos = list(self.educativo_service.archivos_collection.find(filtro_educativo))
                
                for archivo in archivos_educativos:
                    resultados.append({
                        "id": str(archivo['_id']),
                        "tipo_archivo": "educativo",
                        "usuario_id": archivo['usuario_id'],
                        "tipo_usuario": archivo['tipo_usuario'],
                        "nombre_original": archivo['nombre_original'],
                        "nombre_almacenado": archivo['nombre_almacenado'],
                        "url": archivo['url'],
                        "tipo": archivo['tipo'],
                        "peso": archivo['peso'],
                        "modulo_origen": archivo['modulo_origen'],
                        "referencia_id": archivo['referencia_id'],
                        "fecha_subida": archivo['fecha_subida'].isoformat()
                    })
            
            return self._response_format("success", 200, f"Se encontraron {len(resultados)} archivos", {
                "termino_busqueda": termino_busqueda,
                "total_resultados": len(resultados),
                "resultados": resultados
            })
            
        except Exception as e:
            logger.error(f"Error al buscar archivos: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def obtener_estadisticas_archivos(self):
        """16. Obtener estadísticas de archivos por usuario"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            usuario_id = data.get('usuario_id')
            if not usuario_id:
                return self._response_format("error", 400, "usuario_id es requerido")
            
            # Estadísticas de archivos de contenido
            estadisticas_contenido = self.mongo_service.obtener_estadisticas_usuario(usuario_id)
            
            # Estadísticas de archivos educativos
            archivos_educativos = list(self.educativo_service.archivos_collection.find({"usuario_id": usuario_id}))
            
            estadisticas_educativo = {
                "total_archivos": len(archivos_educativos),
                "total_peso": sum(archivo.get('peso', 0) for archivo in archivos_educativos),
                "por_modulo": {}
            }
            
            # Agrupar por módulo
            for archivo in archivos_educativos:
                modulo = archivo.get('modulo_origen', 'sin_modulo')
                if modulo not in estadisticas_educativo["por_modulo"]:
                    estadisticas_educativo["por_modulo"][modulo] = {
                        "archivos": 0,
                        "peso_bytes": 0
                    }
                estadisticas_educativo["por_modulo"][modulo]["archivos"] += 1
                estadisticas_educativo["por_modulo"][modulo]["peso_bytes"] += archivo.get('peso', 0)
            
            return self._response_format("success", 200, "Estadísticas obtenidas exitosamente", {
                "usuario_id": usuario_id,
                "archivos_contenido": estadisticas_contenido,
                "archivos_educativos": estadisticas_educativo,
                "resumen_total": {
                    "total_archivos": estadisticas_contenido.get("total_archivos", 0) + estadisticas_educativo["total_archivos"],
                    "total_peso_bytes": estadisticas_contenido.get("total_peso", 0) + estadisticas_educativo["total_peso"]
                }
            })
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de archivos: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def _verificar_carpetas_usuario(self, usuario_id: str):
        """Verifica y crea las carpetas del usuario si no existen"""
        carpeta_existente = self.mongo_service.obtener_carpeta_usuario(usuario_id)
        
        if not carpeta_existente:
            # Crear registro de carpetas
            documento_carpeta = CarpetaUsuarioModel.crear_documento_carpeta(usuario_id)
            self.mongo_service.crear_carpeta_usuario(documento_carpeta)
            
            # Crear carpetas en MEGA
            self.mega_service.crear_carpeta(f"/Contenido Personal/{usuario_id}/")
            self.mega_service.crear_carpeta(f"/Contenido Educativo/{usuario_id}/")
