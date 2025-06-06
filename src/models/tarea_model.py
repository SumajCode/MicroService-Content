from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class TareaModel:
    def __init__(self):
        self.collection_name = "tareas"
    
    @staticmethod
    def crear_documento_tarea(
        id_tema: str,
        titulo: str,
        descripcion: str,
        fecha_entrega: str,
        archivos: List[Dict] = None
    ) -> Dict:
        """Crea un documento para insertar en MongoDB"""
        return {
            "id_tema": id_tema,
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha_entrega": fecha_entrega,
            "archivos": archivos or [],
            "fecha_creacion": datetime.utcnow(),
            "estado": "activo"
        }
    
    @staticmethod
    def validar_datos_tarea(data: Dict) -> tuple[bool, str]:
        """Valida los datos de la tarea"""
        if not data.get('id_tema'):
            return False, "id_tema es requerido"
        if not data.get('titulo'):
            return False, "titulo es requerido"
        if not data.get('descripcion'):
            return False, "descripcion es requerida"
        if not data.get('fecha_entrega'):
            return False, "fecha_entrega es requerida"
        return True, ""
