from flask import request, jsonify
from src.services.educativo_service import EducativoService
from src.services.mega_service import MegaService
from src.models.publicacion_model import PublicacionModel
from src.utils.file_utils import FileUtils
from src.config.settings import Config
import logging
import tempfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class PublicacionController:
    def __init__(self):
        self.educativo_service = EducativoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.publicacion_model = PublicacionModel()
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    def obtener_publicaciones(self):
        """Obtener publicaciones por tema"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            id_tema = data.get('id_tema')
            if not id_tema:
                return self._response_format("error", 400, "id_tema es requerido")
            
            publicaciones = self.educativo_service.obtener_publicaciones_por_tema(id_tema)
            
            # Formatear respuesta
            publicaciones_formateadas = []
            for pub in publicaciones:
                publicaciones_formateadas.append({
                    "id": str(pub['_id']),
                    "id_tema": pub['id_tema'],
                    "titulo": pub['titulo'],
                    "contenido": pub['contenido'],
                    "archivos": pub.get('archivos', []),
                    "fecha_creacion": pub['fecha_creacion'].isoformat()
                })
            
            return self._response_format("success", 200, "Publicaciones obtenidas exitosamente", {
                "id_tema": id_tema,
                "total_publicaciones": len(publicaciones_formateadas),
                "publicaciones": publicaciones_formateadas
            })
            
        except Exception as e:
            logger.error(f"Error al obtener publicaciones: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def crear_publicacion(self):
        """Crear una nueva publicación"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            # Validar datos
            es_valido, mensaje = PublicacionModel.validar_datos_publicacion(data)
            if not es_valido:
                return self._response_format("error", 400, mensaje)
            
            # Crear documento
            documento = PublicacionModel.crear_documento_publicacion(
                id_tema=data['id_tema'],
                titulo=data['titulo'],
                contenido=data['contenido'],
                archivos=data.get('archivos', [])
            )
            
            # Insertar en base de datos
            publicacion_id = self.educativo_service.insertar_publicacion(documento)
            
            return self._response_format("success", 201, "Publicación creada exitosamente", {
                "publicacion_id": publicacion_id,
                "id_tema": data['id_tema'],
                "titulo": data['titulo']
            })
            
        except Exception as e:
            logger.error(f"Error al crear publicación: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def actualizar_publicacion(self):
        """Actualizar una publicación existente"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            publicacion_id = data.get('_id')
            if not publicacion_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Preparar datos de actualización
            datos_actualizacion = {}
            if 'titulo' in data:
                datos_actualizacion['titulo'] = data['titulo']
            if 'contenido' in data:
                datos_actualizacion['contenido'] = data['contenido']
            if 'archivos' in data:
                datos_actualizacion['archivos'] = data['archivos']
            
            if not datos_actualizacion:
                return self._response_format("error", 400, "No hay datos para actualizar")
            
            # Actualizar en base de datos
            actualizado = self.educativo_service.actualizar_publicacion(publicacion_id, datos_actualizacion)
            
            if actualizado:
                return self._response_format("success", 200, "Publicación actualizada exitosamente", {
                    "publicacion_id": publicacion_id,
                    "campos_actualizados": list(datos_actualizacion.keys())
                })
            else:
                return self._response_format("error", 404, "Publicación no encontrada o no se pudo actualizar")
                
        except Exception as e:
            logger.error(f"Error al actualizar publicación: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_publicacion(self):
        """Eliminar una publicación"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            publicacion_id = data.get('_id')
            if not publicacion_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Eliminar publicación (soft delete)
            eliminado = self.educativo_service.eliminar_publicacion(publicacion_id)
            
            if eliminado:
                return self._response_format("success", 200, "Publicación eliminada exitosamente", {
                    "publicacion_id": publicacion_id
                })
            else:
                return self._response_format("error", 404, "Publicación no encontrada o no se pudo eliminar")
                
        except Exception as e:
            logger.error(f"Error al eliminar publicación: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_publicacion(self):
        """Subir archivo para una publicación"""
        try:
            # Validar que se envió un archivo
            if 'archivo' not in request.files:
                return self._response_format("error", 400, "No se envió ningún archivo")
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                return self._response_format("error", 400, "No se seleccionó ningún archivo")
            
            # Obtener datos del formulario
            id_tema = request.form.get('id_tema')
            usuario_id = request.form.get('usuario_id')
            tipo_usuario = request.form.get('tipo_usuario', 'docente')
            
            if not id_tema or not usuario_id:
                return self._response_format("error", 400, "id_tema y usuario_id son requeridos")
            
            # Validaciones
            if not FileUtils.archivo_permitido(archivo.filename):
                return self._response_format("error", 400, "Tipo de archivo no permitido")
            
            # Obtener información del archivo
            archivo_info = FileUtils.obtener_info_archivo(archivo)
            
            # Generar nombre único
            nombre_unico = f"{uuid.uuid4()}_{archivo_info['nombre']}"
            
            # Guardar archivo temporalmente
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                
                # Subir a MEGA en la carpeta "Archivo"
                resultado_mega = self.mega_service.subir_archivo(
                    temp_path, 
                    "/Archivo/", 
                    nombre_unico
                )
                
                if not resultado_mega:
                    return self._response_format("error", 500, "Error al subir archivo a MEGA")
                
                # Crear documento de archivo
                documento_archivo = {
                    "usuario_id": usuario_id,
                    "tipo_usuario": tipo_usuario,
                    "nombre_original": archivo.filename,
                    "nombre_almacenado": nombre_unico,
                    "url": resultado_mega['link'],
                    "tipo": archivo_info['mime'],
                    "peso": archivo_info['peso_bytes'],
                    "modulo_origen": "publicacion",
                    "referencia_id": id_tema,
                    "fecha_subida": datetime.utcnow()
                }
                
                # Guardar en MongoDB
                archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
                
                return self._response_format("success", 201, "Archivo subido exitosamente", {
                    "archivo_id": archivo_id,
                    "nombre_original": archivo.filename,
                    "nombre_almacenado": nombre_unico,
                    "url": resultado_mega['link'],
                    "tipo": archivo_info['mime'],
                    "peso": archivo_info['peso_bytes']
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivo de publicación: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
