from flask import request, jsonify
from services.educativo_service import EducativoService
from models.tema_model import TemaModel
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

class TemaController:
    def __init__(self):
        self.educativo_service = EducativoService(Config.MONGO_URI)
        self.tema_model = TemaModel()
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    def obtener_temas(self):
        """Obtener temas por curso"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            id_curso = data.get('id_curso')
            if not id_curso:
                return self._response_format("error", 400, "id_curso es requerido")
            
            temas = self.educativo_service.obtener_temas_por_curso(id_curso)
            
            # Formatear respuesta
            temas_formateados = []
            for tema in temas:
                temas_formateados.append({
                    "id": str(tema['_id']),
                    "id_curso": tema['id_curso'],
                    "titulo": tema['titulo'],
                    "descripcion": tema['descripcion'],
                    "orden": tema['orden'],
                    "fecha_creacion": tema['fecha_creacion'].isoformat()
                })
            
            return self._response_format("success", 200, "Temas obtenidos exitosamente", {
                "id_curso": id_curso,
                "total_temas": len(temas_formateados),
                "temas": temas_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al obtener temas: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def crear_tema(self):
        """Crear un nuevo tema"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            # Validar datos
            es_valido, mensaje = TemaModel.validar_datos_tema(data)
            if not es_valido:
                return self._response_format("error", 400, mensaje)
            
            # Crear documento
            documento = TemaModel.crear_documento_tema(
                id_curso=data['id_curso'],
                titulo=data['titulo'],
                descripcion=data['descripcion'],
                orden=data.get('orden', 1)
            )
            
            # Insertar en base de datos
            tema_id = self.educativo_service.insertar_tema(documento)
            
            return self._response_format("success", 201, "Tema creado exitosamente", {
                "tema_id": tema_id,
                "id_curso": data['id_curso'],
                "titulo": data['titulo']
            })
            
        except Exception as e:
            logger.error(f"Error al crear tema: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def actualizar_tema(self):
        """Actualizar un tema existente"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            tema_id = data.get('_id')
            if not tema_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Preparar datos de actualización
            datos_actualizacion = {}
            if 'titulo' in data:
                datos_actualizacion['titulo'] = data['titulo']
            if 'descripcion' in data:
                datos_actualizacion['descripcion'] = data['descripcion']
            if 'orden' in data:
                datos_actualizacion['orden'] = data['orden']
            
            if not datos_actualizacion:
                return self._response_format("error", 400, "No hay datos para actualizar")
            
            # Actualizar en base de datos
            actualizado = self.educativo_service.actualizar_tema(tema_id, datos_actualizacion)
            
            if actualizado:
                return self._response_format("success", 200, "Tema actualizado exitosamente", {
                    "tema_id": tema_id,
                    "campos_actualizados": list(datos_actualizacion.keys())
                })
            else:
                return self._response_format("error", 404, "Tema no encontrado o no se pudo actualizar")
                
        except Exception as e:
            logger.error(f"Error al actualizar tema: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_tema(self):
        """Eliminar un tema"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            tema_id = data.get('_id')
            if not tema_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Eliminar tema (soft delete)
            eliminado = self.educativo_service.eliminar_tema(tema_id)
            
            if eliminado:
                return self._response_format("success", 200, "Tema eliminado exitosamente", {
                    "tema_id": tema_id
                })
            else:
                return self._response_format("error", 404, "Tema no encontrado o no se pudo eliminar")
                
        except Exception as e:
            logger.error(f"Error al eliminar tema: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
