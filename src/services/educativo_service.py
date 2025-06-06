from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EducativoService:
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.microservice_content
        
        # Colecciones educativas
        self.temas_collection = self.db.temas
        self.publicaciones_collection = self.db.publicaciones
        self.tareas_collection = self.db.tareas
        self.entregas_collection = self.db.entregas
        self.anuncios_collection = self.db.anuncios
        self.archivos_collection = self.db.archivos
        
        self._crear_indices()
    
    def _crear_indices(self):
        """Crea índices para optimizar las consultas"""
        try:
            # Índices para temas
            self.temas_collection.create_index([("id_curso", ASCENDING)])
            self.temas_collection.create_index([("orden", ASCENDING)])
            
            # Índices para publicaciones
            self.publicaciones_collection.create_index([("id_tema", ASCENDING)])
            
            # Índices para tareas
            self.tareas_collection.create_index([("id_tema", ASCENDING)])
            self.tareas_collection.create_index([("fecha_entrega", ASCENDING)])
            
            # Índices para entregas
            self.entregas_collection.create_index([("id_tarea", ASCENDING)])
            self.entregas_collection.create_index([("id_estudiante", ASCENDING)])
            self.entregas_collection.create_index([("id_tarea", ASCENDING), ("id_estudiante", ASCENDING)])
            
            # Índices para anuncios
            self.anuncios_collection.create_index([("id_curso", ASCENDING)])
            self.anuncios_collection.create_index([("fecha_creacion", ASCENDING)])
            
            # Índices para archivos
            self.archivos_collection.create_index([("modulo_origen", ASCENDING)])
            self.archivos_collection.create_index([("referencia_id", ASCENDING)])
            
            logger.info("Índices educativos creados exitosamente")
        except Exception as e:
            logger.error(f"Error al crear índices educativos: {e}")
    
    # MÉTODOS PARA TEMAS
    def insertar_tema(self, documento: Dict) -> str:
        try:
            resultado = self.temas_collection.insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar tema: {e}")
            raise
    
    def obtener_temas_por_curso(self, id_curso: str) -> List[Dict]:
        try:
            temas = list(self.temas_collection.find({
                "id_curso": id_curso,
                "estado": "activo"
            }).sort("orden", 1))
            return temas
        except Exception as e:
            logger.error(f"Error al obtener temas: {e}")
            return []
    
    def actualizar_tema(self, tema_id: str, datos: Dict) -> bool:
        try:
            datos["fecha_modificacion"] = datetime.utcnow()
            resultado = self.temas_collection.update_one(
                {"_id": ObjectId(tema_id)},
                {"$set": datos}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar tema: {e}")
            return False
    
    def eliminar_tema(self, tema_id: str) -> bool:
        try:
            resultado = self.temas_collection.update_one(
                {"_id": ObjectId(tema_id)},
                {"$set": {"estado": "eliminado", "fecha_eliminacion": datetime.utcnow()}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar tema: {e}")
            return False
    
    # MÉTODOS PARA PUBLICACIONES
    def insertar_publicacion(self, documento: Dict) -> str:
        try:
            resultado = self.publicaciones_collection.insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar publicación: {e}")
            raise
    
    def obtener_publicaciones_por_tema(self, id_tema: str) -> List[Dict]:
        try:
            publicaciones = list(self.publicaciones_collection.find({
                "id_tema": id_tema,
                "estado": "activo"
            }).sort("fecha_creacion", -1))
            return publicaciones
        except Exception as e:
            logger.error(f"Error al obtener publicaciones: {e}")
            return []
    
    def actualizar_publicacion(self, publicacion_id: str, datos: Dict) -> bool:
        try:
            datos["fecha_modificacion"] = datetime.utcnow()
            resultado = self.publicaciones_collection.update_one(
                {"_id": ObjectId(publicacion_id)},
                {"$set": datos}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar publicación: {e}")
            return False
    
    def eliminar_publicacion(self, publicacion_id: str) -> bool:
        try:
            resultado = self.publicaciones_collection.update_one(
                {"_id": ObjectId(publicacion_id)},
                {"$set": {"estado": "eliminado", "fecha_eliminacion": datetime.utcnow()}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar publicación: {e}")
            return False
    
    # MÉTODOS PARA TAREAS
    def insertar_tarea(self, documento: Dict) -> str:
        try:
            resultado = self.tareas_collection.insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar tarea: {e}")
            raise
    
    def obtener_tareas_por_tema(self, id_tema: str) -> List[Dict]:
        try:
            tareas = list(self.tareas_collection.find({
                "id_tema": id_tema,
                "estado": "activo"
            }).sort("fecha_entrega", 1))
            return tareas
        except Exception as e:
            logger.error(f"Error al obtener tareas: {e}")
            return []
    
    def actualizar_tarea(self, tarea_id: str, datos: Dict) -> bool:
        try:
            datos["fecha_modificacion"] = datetime.utcnow()
            resultado = self.tareas_collection.update_one(
                {"_id": ObjectId(tarea_id)},
                {"$set": datos}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar tarea: {e}")
            return False
    
    def eliminar_tarea(self, tarea_id: str) -> bool:
        try:
            resultado = self.tareas_collection.update_one(
                {"_id": ObjectId(tarea_id)},
                {"$set": {"estado": "eliminado", "fecha_eliminacion": datetime.utcnow()}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar tarea: {e}")
            return False
    
    # MÉTODOS PARA ENTREGAS
    def insertar_entrega(self, documento: Dict) -> str:
        try:
            resultado = self.entregas_collection.insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar entrega: {e}")
            raise
    
    def obtener_entregas_por_tarea(self, id_tarea: str) -> List[Dict]:
        try:
            entregas = list(self.entregas_collection.find({
                "id_tarea": id_tarea
            }).sort("fecha_entrega", -1))
            return entregas
        except Exception as e:
            logger.error(f"Error al obtener entregas: {e}")
            return []
    
    def obtener_entrega_estudiante(self, id_tarea: str, id_estudiante: str) -> Optional[Dict]:
        try:
            entrega = self.entregas_collection.find_one({
                "id_tarea": id_tarea,
                "id_estudiante": id_estudiante
            })
            return entrega
        except Exception as e:
            logger.error(f"Error al obtener entrega del estudiante: {e}")
            return None
    
    def actualizar_entrega(self, entrega_id: str, datos: Dict) -> bool:
        try:
            datos["fecha_modificacion"] = datetime.utcnow()
            resultado = self.entregas_collection.update_one(
                {"_id": ObjectId(entrega_id)},
                {"$set": datos}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar entrega: {e}")
            return False
    
    # MÉTODOS PARA ANUNCIOS
    def insertar_anuncio(self, documento: Dict) -> str:
        try:
            resultado = self.anuncios_collection.insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar anuncio: {e}")
            raise
    
    def obtener_anuncios_por_curso(self, id_curso: str) -> List[Dict]:
        try:
            anuncios = list(self.anuncios_collection.find({
                "id_curso": id_curso,
                "estado": "activo"
            }).sort("fecha_creacion", -1))
            return anuncios
        except Exception as e:
            logger.error(f"Error al obtener anuncios: {e}")
            return []
    
    def actualizar_anuncio(self, anuncio_id: str, datos: Dict) -> bool:
        try:
            datos["fecha_modificacion"] = datetime.utcnow()
            resultado = self.anuncios_collection.update_one(
                {"_id": ObjectId(anuncio_id)},
                {"$set": datos}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al actualizar anuncio: {e}")
            return False
    
    def eliminar_anuncio(self, anuncio_id: str) -> bool:
        try:
            resultado = self.anuncios_collection.update_one(
                {"_id": ObjectId(anuncio_id)},
                {"$set": {"estado": "eliminado", "fecha_eliminacion": datetime.utcnow()}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar anuncio: {e}")
            return False
    
    # MÉTODOS PARA ARCHIVOS EDUCATIVOS
    def insertar_archivo_educativo(self, documento: Dict) -> str:
        try:
            resultado = self.archivos_collection.insert_one(documento)
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar archivo educativo: {e}")
            raise
    
    def obtener_archivos_por_modulo(self, modulo_origen: str, referencia_id: str) -> List[Dict]:
        try:
            archivos = list(self.archivos_collection.find({
                "modulo_origen": modulo_origen,
                "referencia_id": referencia_id
            }).sort("fecha_subida", -1))
            return archivos
        except Exception as e:
            logger.error(f"Error al obtener archivos por módulo: {e}")
            return []
    
    def obtener_archivos_por_usuario(self, usuario_id: str, tipo_usuario: str) -> List[Dict]:
        try:
            archivos = list(self.archivos_collection.find({
                "usuario_id": usuario_id,
                "tipo_usuario": tipo_usuario
            }).sort("fecha_subida", -1))
            return archivos
        except Exception as e:
            logger.error(f"Error al obtener archivos por usuario: {e}")
            return []
    
    def eliminar_archivo_educativo(self, archivo_id: str) -> bool:
        try:
            resultado = self.archivos_collection.delete_one({"_id": ObjectId(archivo_id)})
            return resultado.deleted_count > 0
        except Exception as e:
            logger.error(f"Error al eliminar archivo educativo: {e}")
            return False
    
    def cerrar_conexion(self):
        """Cierra la conexión a MongoDB"""
        try:
            self.client.close()
            logger.info("Conexión educativa a MongoDB cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión educativa: {e}")
