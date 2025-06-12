from flask import request, jsonify
from src.services.educativo_service import EducativoService
from src.services.mega_service import MegaService
from src.models.entrega_model import EntregaModel
from src.utils.file_utils import FileUtils
from src.config.settings import Config
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
        """Subir múltiples archivos para una entrega"""
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
                        
                        archivos_subidos.append({
                            "archivo_id": archivo_id,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes']
                        })
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
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
