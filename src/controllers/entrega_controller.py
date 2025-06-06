from flask import request, jsonify
from services.educativo_service import EducativoService
from services.mega_service import MegaService
from models.entrega_model import EntregaModel
from utils.file_utils import FileUtils
from config.settings import Config
import logging
import tempfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class EntregaController:
    def __init__(self):
        self.educativo_service = EducativoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.entrega_model = EntregaModel()
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    def obtener_entregas(self):
        """Obtener entregas por tarea y estudiante"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            id_tarea = data.get('id_tarea')
            id_estudiante = data.get('id_estudiante')
            
            if not id_tarea:
                return self._response_format("error", 400, "id_tarea es requerido")
            
            if id_estudiante:
                # Obtener entrega específica de un estudiante
                entrega = self.educativo_service.obtener_entrega_estudiante(id_tarea, id_estudiante)
                if entrega:
                    entrega_formateada = {
                        "id": str(entrega['_id']),
                        "id_tarea": entrega['id_tarea'],
                        "id_estudiante": entrega['id_estudiante'],
                        "respuesta": entrega['respuesta'],
                        "archivos": entrega.get('archivos', []),
                        "fecha_entrega": entrega['fecha_entrega'].isoformat(),
                        "estado": entrega.get('estado', 'entregado')
                    }
                    return self._response_format("success", 200, "Entrega obtenida exitosamente", {
                        "entrega": entrega_formateada
                    })
                else:
                    return self._response_format("error", 404, "Entrega no encontrada")
            else:
                # Obtener todas las entregas de una tarea
                entregas = self.educativo_service.obtener_entregas_por_tarea(id_tarea)
                
                entregas_formateadas = []
                for entrega in entregas:
                    entregas_formateadas.append({
                        "id": str(entrega['_id']),
                        "id_tarea": entrega['id_tarea'],
                        "id_estudiante": entrega['id_estudiante'],
                        "respuesta": entrega['respuesta'],
                        "archivos": entrega.get('archivos', []),
                        "fecha_entrega": entrega['fecha_entrega'].isoformat(),
                        "estado": entrega.get('estado', 'entregado')
                    })
                
                return self._response_format("success", 200, "Entregas obtenidas exitosamente", {
                    "id_tarea": id_tarea,
                    "total_entregas": len(entregas_formateadas),
                    "entregas": entregas_formateadas
                })
            
        except Exception as e:
            logger.error(f"Error al obtener entregas: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def crear_entrega(self):
        """Crear una nueva entrega"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            # Validar datos
            es_valido, mensaje = EntregaModel.validar_datos_entrega(data)
            if not es_valido:
                return self._response_format("error", 400, mensaje)
            
            # Verificar si ya existe una entrega del estudiante para esta tarea
            entrega_existente = self.educativo_service.obtener_entrega_estudiante(
                data['id_tarea'], 
                data['id_estudiante']
            )
            
            if entrega_existente:
                return self._response_format("error", 400, "Ya existe una entrega para esta tarea")
            
            # Crear documento
            documento = EntregaModel.crear_documento_entrega(
                id_tarea=data['id_tarea'],
                id_estudiante=data['id_estudiante'],
                respuesta=data['respuesta'],
                archivos=data.get('archivos', [])
            )
            
            # Insertar en base de datos
            entrega_id = self.educativo_service.insertar_entrega(documento)
            
            return self._response_format("success", 201, "Entrega creada exitosamente", {
                "entrega_id": entrega_id,
                "id_tarea": data['id_tarea'],
                "id_estudiante": data['id_estudiante']
            })
            
        except Exception as e:
            logger.error(f"Error al crear entrega: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def actualizar_entrega(self):
        """Actualizar una entrega existente"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            entrega_id = data.get('_id')
            if not entrega_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Preparar datos de actualización
            datos_actualizacion = {}
            if 'respuesta' in data:
                datos_actualizacion['respuesta'] = data['respuesta']
            if 'archivos' in data:
                datos_actualizacion['archivos'] = data['archivos']
            if 'estado' in data:
                datos_actualizacion['estado'] = data['estado']
            
            if not datos_actualizacion:
                return self._response_format("error", 400, "No hay datos para actualizar")
            
            # Actualizar en base de datos
            actualizado = self.educativo_service.actualizar_entrega(entrega_id, datos_actualizacion)
            
            if actualizado:
                return self._response_format("success", 200, "Entrega actualizada exitosamente", {
                    "entrega_id": entrega_id,
                    "campos_actualizados": list(datos_actualizacion.keys())
                })
            else:
                return self._response_format("error", 404, "Entrega no encontrada o no se pudo actualizar")
                
        except Exception as e:
            logger.error(f"Error al actualizar entrega: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_entrega(self):
        """Subir archivo para una entrega"""
        try:
            # Validar que se envió un archivo
            if 'archivo' not in request.files:
                return self._response_format("error", 400, "No se envió ningún archivo")
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                return self._response_format("error", 400, "No se seleccionó ningún archivo")
            
            # Obtener datos del formulario
            id_tarea = request.form.get('id_tarea')
            id_estudiante = request.form.get('id_estudiante')
            
            if not id_tarea or not id_estudiante:
                return self._response_format("error", 400, "id_tarea e id_estudiante son requeridos")
            
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
                    "usuario_id": id_estudiante,
                    "tipo_usuario": "estudiante",
                    "nombre_original": archivo.filename,
                    "nombre_almacenado": nombre_unico,
                    "url": resultado_mega['link'],
                    "tipo": archivo_info['mime'],
                    "peso": archivo_info['peso_bytes'],
                    "modulo_origen": "entrega",
                    "referencia_id": id_tarea,
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
            logger.error(f"Error al subir archivo de entrega: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
