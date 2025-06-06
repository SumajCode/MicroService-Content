from flask import request, jsonify
from services.educativo_service import EducativoService
from services.mega_service import MegaService
from models.tarea_model import TareaModel
from utils.file_utils import FileUtils
from config.settings import Config
import logging
import tempfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class TareaController:
    def __init__(self):
        self.educativo_service = EducativoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.tarea_model = TareaModel()
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    def obtener_tareas(self):
        """Obtener tareas por tema"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            id_tema = data.get('id_tema')
            if not id_tema:
                return self._response_format("error", 400, "id_tema es requerido")
            
            tareas = self.educativo_service.obtener_tareas_por_tema(id_tema)
            
            # Formatear respuesta
            tareas_formateadas = []
            for tarea in tareas:
                tareas_formateadas.append({
                    "id": str(tarea['_id']),
                    "id_tema": tarea['id_tema'],
                    "titulo": tarea['titulo'],
                    "descripcion": tarea['descripcion'],
                    "fecha_entrega": tarea['fecha_entrega'],
                    "archivos": tarea.get('archivos', []),
                    "fecha_creacion": tarea['fecha_creacion'].isoformat()
                })
            
            return self._response_format("success", 200, "Tareas obtenidas exitosamente", {
                "id_tema": id_tema,
                "total_tareas": len(tareas_formateadas),
                "tareas": tareas_formateadas
            })
            
        except Exception as e:
            logger.error(f"Error al obtener tareas: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def crear_tarea(self):
        """Crear una nueva tarea"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            # Validar datos
            es_valido, mensaje = TareaModel.validar_datos_tarea(data)
            if not es_valido:
                return self._response_format("error", 400, mensaje)
            
            # Crear documento
            documento = TareaModel.crear_documento_tarea(
                id_tema=data['id_tema'],
                titulo=data['titulo'],
                descripcion=data['descripcion'],
                fecha_entrega=data['fecha_entrega'],
                archivos=data.get('archivos', [])
            )
            
            # Insertar en base de datos
            tarea_id = self.educativo_service.insertar_tarea(documento)
            
            return self._response_format("success", 201, "Tarea creada exitosamente", {
                "tarea_id": tarea_id,
                "id_tema": data['id_tema'],
                "titulo": data['titulo']
            })
            
        except Exception as e:
            logger.error(f"Error al crear tarea: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def actualizar_tarea(self):
        """Actualizar una tarea existente"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            tarea_id = data.get('_id')
            if not tarea_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Preparar datos de actualización
            datos_actualizacion = {}
            if 'titulo' in data:
                datos_actualizacion['titulo'] = data['titulo']
            if 'descripcion' in data:
                datos_actualizacion['descripcion'] = data['descripcion']
            if 'fecha_entrega' in data:
                datos_actualizacion['fecha_entrega'] = data['fecha_entrega']
            if 'archivos' in data:
                datos_actualizacion['archivos'] = data['archivos']
            
            if not datos_actualizacion:
                return self._response_format("error", 400, "No hay datos para actualizar")
            
            # Actualizar en base de datos
            actualizado = self.educativo_service.actualizar_tarea(tarea_id, datos_actualizacion)
            
            if actualizado:
                return self._response_format("success", 200, "Tarea actualizada exitosamente", {
                    "tarea_id": tarea_id,
                    "campos_actualizados": list(datos_actualizacion.keys())
                })
            else:
                return self._response_format("error", 404, "Tarea no encontrada o no se pudo actualizar")
                
        except Exception as e:
            logger.error(f"Error al actualizar tarea: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_tarea(self):
        """Eliminar una tarea"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            tarea_id = data.get('_id')
            if not tarea_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Eliminar tarea (soft delete)
            eliminado = self.educativo_service.eliminar_tarea(tarea_id)
            
            if eliminado:
                return self._response_format("success", 200, "Tarea eliminada exitosamente", {
                    "tarea_id": tarea_id
                })
            else:
                return self._response_format("error", 404, "Tarea no encontrada o no se pudo eliminar")
                
        except Exception as e:
            logger.error(f"Error al eliminar tarea: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_tarea(self):
        """Subir archivo para una tarea"""
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
                    "modulo_origen": "tarea",
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
            logger.error(f"Error al subir archivo de tarea: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
