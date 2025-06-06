from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoService:
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.microservice_content
        self.archivos_collection = self.db.archivos_subidos
        self.carpetas_collection = self.db.carpetas_usuarios
        self._crear_indices()
    
    def _crear_indices(self):
        """Crea índices para optimizar las consultas"""
        try:
            # Índices para archivos_subidos
            self.archivos_collection.create_index([("usuario_id", ASCENDING)])
            self.archivos_collection.create_index([("carpeta", ASCENDING)])
            self.archivos_collection.create_index([("archivo.mega_node_id", ASCENDING)])
            self.archivos_collection.create_index([("estado", ASCENDING)])
            self.archivos_collection.create_index([("usuario_id", ASCENDING), ("carpeta", ASCENDING)])
            
            # Índices para carpetas_usuarios
            self.carpetas_collection.create_index([("usuario_id", ASCENDING)], unique=True)
            
            logger.info("Índices de MongoDB creados exitosamente")
        except Exception as e:
            logger.error(f"Error al crear índices: {e}")
    
    def insertar_archivo(self, documento: Dict) -> str:
        """Inserta un nuevo archivo en la base de datos"""
        try:
            resultado = self.archivos_collection.insert_one(documento)
            logger.info(f"Archivo insertado con ID: {resultado.inserted_id}")
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al insertar archivo: {e}")
            raise
    
    def obtener_archivo_por_id(self, archivo_id: str) -> Optional[Dict]:
        """Obtiene un archivo por su ID"""
        try:
            archivo = self.archivos_collection.find_one({"_id": ObjectId(archivo_id)})
            return archivo
        except Exception as e:
            logger.error(f"Error al obtener archivo por ID: {e}")
            return None
    
    def obtener_archivos_usuario_carpeta(self, usuario_id: str, carpeta: str) -> List[Dict]:
        """Obtiene todos los archivos de un usuario en una carpeta específica"""
        try:
            archivos = list(self.archivos_collection.find({
                "usuario_id": usuario_id,
                "carpeta": carpeta,
                "estado": "activo"
            }).sort("fecha_subida", -1))
            return archivos
        except Exception as e:
            logger.error(f"Error al obtener archivos del usuario: {e}")
            return []
    
    def obtener_todos_archivos_usuario(self, usuario_id: str) -> List[Dict]:
        """Obtiene todos los archivos de un usuario (todas las carpetas)"""
        try:
            archivos = list(self.archivos_collection.find({
                "usuario_id": usuario_id,
                "estado": "activo"
            }).sort("fecha_subida", -1))
            return archivos
        except Exception as e:
            logger.error(f"Error al obtener todos los archivos del usuario: {e}")
            return []
    
    def actualizar_archivo(self, archivo_id: str, datos_actualizacion: Dict) -> bool:
        """Actualiza los metadatos de un archivo"""
        try:
            # Agregar fecha de modificación
            datos_actualizacion["fecha_modificacion"] = datetime.utcnow()
            
            resultado = self.archivos_collection.update_one(
                {"_id": ObjectId(archivo_id)},
                {"$set": datos_actualizacion}
            )
            
            if resultado.modified_count > 0:
                logger.info(f"Archivo {archivo_id} actualizado exitosamente")
                return True
            else:
                logger.warning(f"No se pudo actualizar el archivo {archivo_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error al actualizar archivo: {e}")
            return False
    
    def eliminar_archivo(self, archivo_id: str) -> bool:
        """Marca un archivo como eliminado (soft delete)"""
        try:
            resultado = self.archivos_collection.update_one(
                {"_id": ObjectId(archivo_id)},
                {
                    "$set": {
                        "estado": "eliminado",
                        "fecha_eliminacion": datetime.utcnow()
                    }
                }
            )
            
            if resultado.modified_count > 0:
                logger.info(f"Archivo {archivo_id} marcado como eliminado")
                return True
            else:
                logger.warning(f"No se pudo eliminar el archivo {archivo_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False
    
    def eliminar_archivo_permanente(self, archivo_id: str) -> bool:
        """Elimina un archivo permanentemente de la base de datos"""
        try:
            resultado = self.archivos_collection.delete_one({"_id": ObjectId(archivo_id)})
            
            if resultado.deleted_count > 0:
                logger.info(f"Archivo {archivo_id} eliminado permanentemente")
                return True
            else:
                logger.warning(f"No se pudo eliminar permanentemente el archivo {archivo_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo permanentemente: {e}")
            return False
    
    def eliminar_datos_usuario(self, usuario_id: str) -> bool:
        """Elimina todos los datos de un usuario"""
        try:
            # Eliminar todos los archivos del usuario
            resultado_archivos = self.archivos_collection.delete_many({"usuario_id": usuario_id})
            
            # Eliminar registro de carpetas del usuario
            resultado_carpetas = self.carpetas_collection.delete_one({"usuario_id": usuario_id})
            
            logger.info(f"Eliminados {resultado_archivos.deleted_count} archivos y {resultado_carpetas.deleted_count} registro de carpetas para usuario {usuario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar datos del usuario: {e}")
            return False
    
    def crear_carpeta_usuario(self, documento: Dict) -> str:
        """Crea el registro de carpetas para un usuario"""
        try:
            resultado = self.carpetas_collection.insert_one(documento)
            logger.info(f"Carpetas de usuario creadas con ID: {resultado.inserted_id}")
            return str(resultado.inserted_id)
        except Exception as e:
            logger.error(f"Error al crear carpetas de usuario: {e}")
            raise
    
    def obtener_carpeta_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Obtiene el registro de carpetas de un usuario"""
        try:
            carpeta = self.carpetas_collection.find_one({"usuario_id": usuario_id})
            return carpeta
        except Exception as e:
            logger.error(f"Error al obtener carpetas del usuario: {e}")
            return None
    
    def verificar_archivo_existe(self, usuario_id: str, nombre_archivo: str, carpeta: str) -> bool:
        """Verifica si un archivo ya existe para un usuario en una carpeta específica"""
        try:
            archivo = self.archivos_collection.find_one({
                "usuario_id": usuario_id,
                "archivo.nombre": nombre_archivo,
                "carpeta": carpeta,
                "estado": "activo"
            })
            return archivo is not None
        except Exception as e:
            logger.error(f"Error al verificar existencia del archivo: {e}")
            return False
    
    def obtener_estadisticas_usuario(self, usuario_id: str) -> Dict:
        """Obtiene estadísticas de archivos de un usuario"""
        try:
            pipeline = [
                {"$match": {"usuario_id": usuario_id, "estado": "activo"}},
                {
                    "$group": {
                        "_id": "$carpeta",
                        "total_archivos": {"$sum": 1},
                        "total_peso": {"$sum": "$archivo.peso"}
                    }
                }
            ]
            
            resultados = list(self.archivos_collection.aggregate(pipeline))
            
            estadisticas = {
                "usuario_id": usuario_id,
                "carpetas": {},
                "total_archivos": 0,
                "total_peso": 0
            }
            
            for resultado in resultados:
                carpeta = resultado["_id"]
                estadisticas["carpetas"][carpeta] = {
                    "archivos": resultado["total_archivos"],
                    "peso_bytes": resultado["total_peso"]
                }
                estadisticas["total_archivos"] += resultado["total_archivos"]
                estadisticas["total_peso"] += resultado["total_peso"]
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas del usuario: {e}")
            return {}
    
    def buscar_archivos(self, usuario_id: str, termino_busqueda: str, carpeta: Optional[str] = None) -> List[Dict]:
        """Busca archivos por nombre"""
        try:
            filtro = {
                "usuario_id": usuario_id,
                "estado": "activo",
                "archivo.nombre": {"$regex": termino_busqueda, "$options": "i"}
            }
            
            if carpeta:
                filtro["carpeta"] = carpeta
            
            archivos = list(self.archivos_collection.find(filtro).sort("fecha_subida", -1))
            return archivos
            
        except Exception as e:
            logger.error(f"Error al buscar archivos: {e}")
            return []
    
    def cerrar_conexion(self):
        """Cierra la conexión a MongoDB"""
        try:
            self.client.close()
            logger.info("Conexión a MongoDB cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión: {e}")
