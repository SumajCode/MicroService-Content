from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MongoService:
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_default_database()
        self.archivos_collection = self.db.archivos_subidos
        self.carpetas_collection = self.db.carpetas_usuarios
    
    def insertar_archivo(self, documento: Dict) -> str:
        """Inserta un nuevo archivo en la colección"""
        try:
            result = self.archivos_collection.insert_one(documento)
            logger.info(f"Archivo insertado con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error al insertar archivo: {e}")
            raise
    
    def obtener_archivo_por_id(self, archivo_id: str) -> Optional[Dict]:
        """Obtiene un archivo por su ID"""
        try:
            return self.archivos_collection.find_one({"_id": ObjectId(archivo_id)})
        except PyMongoError as e:
            logger.error(f"Error al obtener archivo: {e}")
            return None
    
    def actualizar_archivo(self, archivo_id: str, datos_actualizacion: Dict) -> bool:
        """Actualiza un archivo existente"""
        try:
            result = self.archivos_collection.update_one(
                {"_id": ObjectId(archivo_id)},
                {"$set": datos_actualizacion}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error al actualizar archivo: {e}")
            return False
    
    def eliminar_archivo(self, archivo_id: str) -> bool:
        """Marca un archivo como eliminado"""
        try:
            result = self.archivos_collection.update_one(
                {"_id": ObjectId(archivo_id)},
                {"$set": {"estado": "eliminado"}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False
    
    def obtener_carpeta_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Obtiene las carpetas de un usuario"""
        try:
            return self.carpetas_collection.find_one({"usuario_id": usuario_id})
        except PyMongoError as e:
            logger.error(f"Error al obtener carpetas del usuario: {e}")
            return None
    
    def crear_carpeta_usuario(self, documento: Dict) -> str:
        """Crea registro de carpetas para un usuario"""
        try:
            result = self.carpetas_collection.insert_one(documento)
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error al crear carpetas de usuario: {e}")
            raise
    
    def eliminar_datos_usuario(self, usuario_id: str) -> bool:
        """Elimina todos los datos de un usuario"""
        try:
            # Eliminar archivos
            self.archivos_collection.delete_many({"usuario_id": usuario_id})
            # Eliminar carpetas
            self.carpetas_collection.delete_many({"usuario_id": usuario_id})
            logger.info(f"Datos del usuario {usuario_id} eliminados")
            return True
        except PyMongoError as e:
            logger.error(f"Error al eliminar datos del usuario: {e}")
            return False
    
    def obtener_archivos_usuario(self, usuario_id: str) -> List[Dict]:
        """Obtiene todos los archivos de un usuario"""
        try:
            return list(self.archivos_collection.find({"usuario_id": usuario_id}))
        except PyMongoError as e:
            logger.error(f"Error al obtener archivos del usuario: {e}")
            return []
