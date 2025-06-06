from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class PublicacionModel:
    def __init__(self):
        self.collection_name = "publicaciones"
    
    @staticmethod
    def crear_documento_publicacion(
        id_tema: str,
        titulo: str,
        contenido: str,
        archivos: List[Dict] = None
    ) -> Dict:
        """Crea un documento para insertar en MongoDB"""
        return {
            "id_tema": id_tema,
            "titulo": titulo,
            "contenido": contenido,
            "archivos": archivos or [],
            "fecha_creacion": datetime.utcnow(),
            "estado": "activo"
        }
    
    @staticmethod
    def validar_datos_publicacion(data: Dict) -> tuple[bool, str]:
        """Valida los datos de la publicación"""
        if not data.get('id_tema'):
            return False, "id_tema es requerido"
        if not data.get('titulo'):
            return False, "titulo es requerido"
        if not data.get('contenido'):
            return False, "contenido es requerido"
        return True, ""
