from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from services.mongo_service import MongoService
from services.mega_service import MegaService
from services.api_externa_service import ApiExternaService
from models.archivo_model import ArchivoModel, CarpetaUsuarioModel
from utils.file_utils import FileUtils
from config.settings import Config
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

class ArchivoController:
    def __init__(self):
        self.mongo_service = MongoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.api_externa = ApiExternaService(Config.API_USUARIOS_URL)
        self.archivo_model = ArchivoModel()
        self.carpeta_model = CarpetaUsuarioModel()
    
    def subir_archivo(self):
        """Endpoint para subir archivos"""
        try:
            # Validar que se envió un archivo
            if 'archivo' not in request.files:
                return jsonify({"error": "No se envió ningún archivo"}), 400
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
            # Obtener datos del formulario
            usuario_id = request.form.get('usuario_id')
            tipo_contenido = request.form.get('tipo_contenido')
            
            if not usuario_id or not tipo_contenido:
                return jsonify({"error": "usuario_id y tipo_contenido son requeridos"}), 400
            
            # Validaciones
            if not FileUtils.archivo_permitido(archivo.filename):
                return jsonify({"error": "Tipo de archivo no permitido"}), 400
            
            if not FileUtils.validar_tipo_contenido(tipo_contenido):
                return jsonify({"error": "Tipo de contenido inválido"}), 400
            
            # Consultar API externa para obtener datos del usuario
            usuario_info = self.api_externa.obtener_usuario(usuario_id)
            if not usuario_info:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Obtener información del archivo
            archivo_info = FileUtils.obtener_info_archivo(archivo)
            
            # Verificar/crear carpetas del usuario
            self._verificar_carpetas_usuario(usuario_id, usuario_info['nombre_usuario'])
            
            # Guardar archivo temporalmente
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                
                # Generar ruta en MEGA
                ruta_mega = FileUtils.generar_ruta_mega(usuario_id, tipo_contenido)
                
                # Subir a MEGA
                link_mega = self.mega_service.subir_archivo(
                    temp_path, 
                    ruta_mega, 
                    archivo_info['nombre']
                )
                
                if not link_mega:
                    return jsonify({"error": "Error al subir archivo a MEGA"}), 500
                
                # Actualizar información del archivo
                archivo_info.update({
                    "link": link_mega,
                    "ruta": ruta_mega + archivo_info['nombre']
                })
                
                # Crear documento para MongoDB
                documento = ArchivoModel.crear_documento_archivo(
                    usuario_id,
                    usuario_info['nombre_usuario'],
                    tipo_contenido,
                    archivo_info
                )
                
                # Guardar en MongoDB
                archivo_id = self.mongo_service.insertar_archivo(documento)
                
                return jsonify({
                    "mensaje": "Archivo subido exitosamente",
                    "archivo_id": archivo_id,
                    "archivo": {
                        "nombre": archivo_info['nombre'],
                        "tipo": archivo_info['mime'],
                        "peso": archivo_info['peso_bytes'],
                        "link": link_mega,
                        "ruta": archivo_info['ruta']
                    }
                }), 201
                
        except Exception as e:
            logger.error(f"Error al subir archivo: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    def reemplazar_archivo(self, archivo_id):
        """Endpoint para reemplazar un archivo existente"""
        try:
            # Verificar que el archivo existe
            archivo_existente = self.mongo_service.obtener_archivo_por_id(archivo_id)
            if not archivo_existente:
                return jsonify({"error": "Archivo no encontrado"}), 404
            
            # Validar que se envió un archivo
            if 'archivo' not in request.files:
                return jsonify({"error": "No se envió ningún archivo"}), 400
            
            nuevo_archivo = request.files['archivo']
            if nuevo_archivo.filename == '':
                return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
            # Validaciones
            if not FileUtils.archivo_permitido(nuevo_archivo.filename):
                return jsonify({"error": "Tipo de archivo no permitido"}), 400
            
            # Eliminar archivo anterior de MEGA
            self.mega_service.eliminar_archivo(archivo_existente['archivo']['ruta'])
            
            # Obtener información del nuevo archivo
            nuevo_archivo_info = FileUtils.obtener_info_archivo(nuevo_archivo)
            
            # Guardar nuevo archivo temporalmente
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = FileUtils.guardar_archivo_temporal(nuevo_archivo, temp_dir)
                
                # Generar ruta en MEGA (misma carpeta que el anterior)
                ruta_mega = FileUtils.generar_ruta_mega(
                    archivo_existente['usuario_id'], 
                    archivo_existente['tipo_contenido']
                )
                
                # Subir nuevo archivo a MEGA
                link_mega = self.mega_service.subir_archivo(
                    temp_path, 
                    ruta_mega, 
                    nuevo_archivo_info['nombre']
                )
                
                if not link_mega:
                    return jsonify({"error": "Error al subir nuevo archivo a MEGA"}), 500
                
                # Actualizar información en MongoDB
                datos_actualizacion = {
                    "archivo.nombre": nuevo_archivo_info['nombre'],
                    "archivo.tipo": nuevo_archivo_info['mime'],
                    "archivo.peso": nuevo_archivo_info['peso_bytes'],
                    "archivo.link": link_mega,
                    "archivo.ruta": ruta_mega + nuevo_archivo_info['nombre']
                }
                
                if self.mongo_service.actualizar_archivo(archivo_id, datos_actualizacion):
                    return jsonify({
                        "mensaje": "Archivo reemplazado exitosamente",
                        "archivo_id": archivo_id,
                        "nuevo_archivo": {
                            "nombre": nuevo_archivo_info['nombre'],
                            "tipo": nuevo_archivo_info['mime'],
                            "peso": nuevo_archivo_info['peso_bytes'],
                            "link": link_mega
                        }
                    }), 200
                else:
                    return jsonify({"error": "Error al actualizar archivo en base de datos"}), 500
                
        except Exception as e:
            logger.error(f"Error al reemplazar archivo: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    def eliminar_archivo(self, archivo_id):
        """Endpoint para eliminar un archivo"""
        try:
            # Verificar que el archivo existe
            archivo = self.mongo_service.obtener_archivo_por_id(archivo_id)
            if not archivo:
                return jsonify({"error": "Archivo no encontrado"}), 404
            
            # Eliminar de MEGA
            if self.mega_service.eliminar_archivo(archivo['archivo']['ruta']):
                # Marcar como eliminado en MongoDB
                if self.mongo_service.eliminar_archivo(archivo_id):
                    return jsonify({"mensaje": "Archivo eliminado exitosamente"}), 200
                else:
                    return jsonify({"error": "Error al actualizar estado en base de datos"}), 500
            else:
                return jsonify({"error": "Error al eliminar archivo de MEGA"}), 500
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    def eliminar_usuario_completo(self, usuario_id):
        """Endpoint para eliminar todo el contenido de un usuario"""
        try:
            # Verificar que el usuario existe
            usuario_info = self.api_externa.obtener_usuario(usuario_id)
            if not usuario_info:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Eliminar carpetas de MEGA
            if self.mega_service.eliminar_carpeta_usuario(usuario_id):
                # Eliminar registros de MongoDB
                if self.mongo_service.eliminar_datos_usuario(usuario_id):
                    return jsonify({
                        "mensaje": f"Todo el contenido del usuario {usuario_id} ha sido eliminado"
                    }), 200
                else:
                    return jsonify({"error": "Error al eliminar datos de la base de datos"}), 500
            else:
                return jsonify({"error": "Error al eliminar carpetas de MEGA"}), 500
                
        except Exception as e:
            logger.error(f"Error al eliminar usuario completo: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    def obtener_archivos_usuario(self, usuario_id):
        """Endpoint para obtener todos los archivos de un usuario"""
        try:
            archivos = self.mongo_service.obtener_archivos_usuario(usuario_id)
            
            # Filtrar archivos activos
            archivos_activos = [
                archivo for archivo in archivos 
                if archivo.get('estado') == 'activo'
            ]
            
            return jsonify({
                "usuario_id": usuario_id,
                "total_archivos": len(archivos_activos),
                "archivos": archivos_activos
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener archivos del usuario: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    def _verificar_carpetas_usuario(self, usuario_id: str, nombre_usuario: str):
        """Verifica y crea las carpetas del usuario si no existen"""
        carpeta_existente = self.mongo_service.obtener_carpeta_usuario(usuario_id)
        
        if not carpeta_existente:
            # Crear registro de carpetas
            documento_carpeta = CarpetaUsuarioModel.crear_documento_carpeta(
                usuario_id, nombre_usuario
            )
            self.mongo_service.crear_carpeta_usuario(documento_carpeta)
            
            # Crear carpetas en MEGA
            self.mega_service.crear_carpeta(f"/Contenido Personal/{usuario_id}/")
            self.mega_service.crear_carpeta(f"/Contenido Educativo/{usuario_id}/")
