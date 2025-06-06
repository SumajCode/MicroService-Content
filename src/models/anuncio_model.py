from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class AnuncioModel:
    def __init__(self):
        self.collection_name = "anuncios"
    
    @staticmethod
    def crear_documento_anuncio(
        id_curso: str,
        titulo: str,
        contenido: str,
        autor_id: str,
        tipo_usuario: str,
        archivos: List[Dict] = None
    ) -> Dict:
        """Crea un documento para insertar en MongoDB"""
        return {
            "id_curso": id_curso,
            "titulo": titulo,
            "contenido": contenido,
            "autor_id": autor_id,
            "tipo_usuario": tipo_usuario,
            "archivos": archivos or [],
            "fecha_creacion": datetime.utcnow(),
            "estado": "activo"
        }
    
    @staticmethod
    def validar_datos_anuncio(data: Dict) -> tuple[bool, str]:
        """Valida los datos del anuncio"""
        if not data.get('id_curso'):
            return False, "id_curso es requerido"
        if not data.get('titulo'):
            return False, "titulo es requerido"
        if not data.get('contenido'):
            return False, "contenido es requerido"
        if not data.get('autor_id'):
            return False, "autor_id es requerido"
        if not data.get('tipo_usuario'):
            return False, "tipo_usuario es requerido"
        return True, ""
