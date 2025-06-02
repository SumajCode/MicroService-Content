from flask import request, jsonify, send_file
from werkzeug.exceptions import BadRequest
from services.mongo_service import MongoService
from services.mega_service import MegaService
from models.archivo_model import ArchivoModel, CarpetaUsuarioModel
from utils.file_utils import FileUtils
from config.settings import Config
import logging
import os
import tempfile
import zipfile
from io import BytesIO

logger = logging.getLogger(__name__)

class ArchivoController:
    def __init__(self):
        self.mongo_service = MongoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
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
    
    def subir_archivo(self):
        """1. Subir un archivo a una carpeta específica"""
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
            logger.error(f"Error al subir archivo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_multiples_archivos(self):
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
            logger.error(f"Error al subir múltiples archivos: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def obtener_info_archivo(self):
        """3. Obtener información de un archivo (devuelve el link)"""
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
            logger.error(f"Error al obtener información del archivo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def listar_archivos_usuario_carpeta(self):
        """4. Listar todos los archivos de un usuario por carpeta"""
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
            logger.error(f"Error al listar archivos del usuario: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def descargar_archivo(self):
        """5. Descargar un archivo"""
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
            logger.error(f"Error al descargar archivo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def descargar_carpeta_zip(self):
        """6. Descargar todos los archivos de la carpeta de un usuario como .zip"""
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
            archivos_activos = [archivo for archivo in archivos if archivo.get('estado') == 'activo']
            
            if not archivos_activos:
                return self._response_format("error", 404, "No hay archivos en esta carpeta")
            
            # Crear ZIP en memoria
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for archivo in archivos_activos:
                    try:
                        # Descargar archivo de MEGA
                        archivo_descargado = self.mega_service.descargar_archivo(archivo['archivo']['mega_node_id'])
                        if archivo_descargado:
                            zip_file.write(archivo_descargado, archivo['archivo']['nombre'])
                    except Exception as e:
                        logger.error(f"Error al agregar archivo {archivo['archivo']['nombre']} al ZIP: {e}")
            
            zip_buffer.seek(0)
            
            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=f"{usuario_id}_{carpeta.replace(' ', '_')}.zip",
                mimetype='application/zip'
            )
            
        except Exception as e:
            logger.error(f"Error al crear ZIP: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def actualizar_metadatos(self):
        """7. Actualizar metadatos del archivo (nombre visible, carpeta, etc.)"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            archivo_id = data.get('fileId')
            usuario_id = data.get('userId')
            nuevo_nombre = data.get('nuevoNombre')
            nueva_carpeta = data.get('nuevaCarpeta')
            
            if not archivo_id or not usuario_id:
                return self._response_format("error", 400, "fileId y userId son requeridos")
            
            # Obtener archivo de la base de datos
            archivo = self.mongo_service.obtener_archivo_por_id(archivo_id)
            if not archivo:
                return self._response_format("error", 404, "Archivo no encontrado")
            
            # Verificar que el archivo pertenece al usuario
            if archivo['usuario_id'] != usuario_id:
                return self._response_format("error", 403, "No tienes permisos para modificar este archivo")
            
            datos_actualizacion = {}
            
            # Actualizar nombre si se proporciona
            if nuevo_nombre:
                datos_actualizacion['archivo.nombre'] = nuevo_nombre
            
            # Mover a nueva carpeta si se proporciona
            if nueva_carpeta:
                if not FileUtils.validar_carpeta(nueva_carpeta):
                    return self._response_format("error", 400, "Nueva carpeta inválida")
                
                # Mover archivo en MEGA
                nueva_ruta = FileUtils.generar_ruta_mega(usuario_id, nueva_carpeta)
                if self.mega_service.mover_archivo(archivo['archivo']['mega_node_id'], nueva_ruta):
                    datos_actualizacion['carpeta'] = nueva_carpeta
                    datos_actualizacion['archivo.ruta'] = nueva_ruta + (nuevo_nombre or archivo['archivo']['nombre'])
                else:
                    return self._response_format("error", 500, "Error al mover archivo en MEGA")
            
            if datos_actualizacion:
                if self.mongo_service.actualizar_archivo(archivo_id, datos_actualizacion):
                    return self._response_format("success", 200, "Metadatos actualizados exitosamente", {
                        "userId": usuario_id,
                        "fileId": archivo_id,
                        "updatedFields": datos_actualizacion
                    })
                else:
                    return self._response_format("error", 500, "Error al actualizar metadatos en base de datos")
            else:
                return self._response_format("error", 400, "No se proporcionaron datos para actualizar")
                
        except Exception as e:
            logger.error(f"Error al actualizar metadatos: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_archivo(self):
        """8. Eliminar un archivo"""
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
                return self._response_format("error", 403, "No tienes permisos para eliminar este archivo")
            
            # Eliminar de MEGA
            if self.mega_service.eliminar_archivo(archivo['archivo']['mega_node_id']):
                # Marcar como eliminado en MongoDB
                if self.mongo_service.eliminar_archivo(archivo_id):
                    return self._response_format("success", 200, "Archivo eliminado exitosamente", {
                        "userId": usuario_id,
                        "fileId": archivo_id
                    })
                else:
                    return self._response_format("error", 500, "Error al actualizar estado en base de datos")
            else:
                return self._response_format("error", 500, "Error al eliminar archivo de MEGA")
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_usuario_completo(self):
        """9. Eliminar todos los archivos y la carpeta de un usuario"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            usuario_id = data.get('userId')
            
            if not usuario_id:
                return self._response_format("error", 400, "userId es requerido")
            
            # Eliminar carpetas de MEGA
            if self.mega_service.eliminar_carpeta_usuario(usuario_id):
                # Eliminar registros de MongoDB
                if self.mongo_service.eliminar_datos_usuario(usuario_id):
                    return self._response_format("success", 200, f"Todo el contenido del usuario {usuario_id} ha sido eliminado", {
                        "userId": usuario_id
                    })
                else:
                    return self._response_format("error", 500, "Error al eliminar datos de la base de datos")
            else:
                return self._response_format("error", 500, "Error al eliminar carpetas de MEGA")
                
        except Exception as e:
            logger.error(f"Error al eliminar usuario completo: {e}")
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
