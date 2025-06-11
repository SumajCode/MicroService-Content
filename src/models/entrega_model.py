from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class EntregaModel:
    def __init__(self):
        self.collection_name = "entregas"
    
    @staticmethod
    def crear_documento_entrega(
        id_tarea: str,
        id_estudiante: str,
        respuesta: str,
        archivos: List[Dict] = None
    ) -> Dict:
        """Crea un documento para insertar en MongoDB"""
        return {
            "id_tarea": id_tarea,
            "id_estudiante": id_estudiante,
            "respuesta": respuesta,
            "archivos": archivos or [],
            "fecha_entrega": datetime.utcnow(),
            "estado": "entregado"
        }
    
    @staticmethod
    def validar_datos_entrega(data: Dict) -> tuple[bool, str]:
        """Valida los datos de la entrega"""
        if not data.get('id_tarea'):
            return False, "id_tarea es requerido"
        if not data.get('id_estudiante'):
            return False, "id_estudiante es requerido"
        if not data.get('respuesta'):
            return False, "respuesta es requerida"
        return True, ""
