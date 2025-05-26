from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class ArchivoModel:
    def __init__(self):
        self.collection_name = "archivos_subidos"
    
    @staticmethod
    def crear_documento_archivo(
        usuario_id: str,
        nombre_usuario: str,
        tipo_contenido: str,
        archivo_info: Dict,
        etiquetas: Optional[List[str]] = None
    ) -> Dict:
        """Crea un documento para insertar en MongoDB"""
        return {
            "usuario_id": usuario_id,
            "nombre_usuario": nombre_usuario,
            "tipo_contenido": tipo_contenido,
            "archivo": {
                "nombre": archivo_info.get("nombre"),
                "tipo": archivo_info.get("mime"),
                "peso": archivo_info.get("peso_bytes"),
                "link": archivo_info.get("link", ""),
                "ruta": archivo_info.get("ruta", "")
            },
            "fecha_subida": datetime.utcnow(),
            "etiquetas": etiquetas or [],
            "estado": "activo"
        }

class CarpetaUsuarioModel:
    def __init__(self):
        self.collection_name = "carpetas_usuarios"
    
    @staticmethod
    def crear_documento_carpeta(usuario_id: str, nombre_usuario: str) -> Dict:
        """Crea un documento para carpetas de usuario"""
        return {
            "usuario_id": usuario_id,
            "nombre_usuario": nombre_usuario,
            "carpetas": {
                "personal": {"ruta": f"/Contenido Personal/{usuario_id}/"},
                "educativo": {"ruta": f"/Contenido Educativo/{usuario_id}/"}
            }
        }
