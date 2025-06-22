from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class TemaModel:
    def __init__(self):
        self.collection_name = "temas"
    
    @staticmethod
    def crear_documento_tema(
        id_curso: str,
        titulo: str,
        descripcion: str,
        orden: int = 1
    ) -> Dict:
        """Crea un documento para insertar en MongoDB"""
        return {
            "id_curso": id_curso,
            "titulo": titulo,
            "descripcion": descripcion,
            "orden": orden,
            "fecha_creacion": datetime.utcnow(),
            "estado": "activo"
        }
    
    @staticmethod
    def validar_datos_tema(data: Dict) -> tuple[bool, str]:
        """Valida los datos del tema"""
        if not data.get('id_curso'):
            return False, "id_curso es requerido"
        if not data.get('titulo'):
            return False, "titulo es requerido"
        if not data.get('descripcion'):
            return False, "descripcion es requerida"
        return True, ""
