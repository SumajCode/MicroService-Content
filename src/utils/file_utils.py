import os
import mimetypes
from werkzeug.utils import secure_filename
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
        'xls', 'xlsx', 'ppt', 'pptx', 'mp4', 'avi', 'mov', 'mp3', 'wav',
        'zip', 'rar', '7z', 'tar', 'gz'
    }
    
    CARPETAS_VALIDAS = ['Contenido Personal', 'Contenido Educativo']
    
    @staticmethod
    def archivo_permitido(filename: str) -> bool:
        """Verifica si el archivo tiene una extensión permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUtils.ALLOWED_EXTENSIONS
    
    @staticmethod
    def obtener_info_archivo(archivo) -> Dict:
        """Extrae información del archivo subido"""
        filename = secure_filename(archivo.filename)
        mime_type = archivo.content_type or mimetypes.guess_type(filename)[0]
        
        # Obtener tamaño del archivo
        archivo.seek(0, os.SEEK_END)
        file_size = archivo.tell()
        archivo.seek(0)  # Volver al inicio
        
        return {
            "nombre": filename,
            "mime": mime_type,
            "peso_bytes": file_size
        }
    
    @staticmethod
    def validar_carpeta(carpeta: str) -> bool:
        """Valida que la carpeta sea válida"""
        return carpeta in FileUtils.CARPETAS_VALIDAS
    
    @staticmethod
    def generar_ruta_mega(usuario_id: str, carpeta: str) -> str:
        """Genera la ruta de carpeta en MEGA"""
        if carpeta == 'Contenido Personal':
            return f"/Contenido Personal/{usuario_id}/"
        elif carpeta == 'Contenido Educativo':
            return f"/Contenido Educativo/{usuario_id}/"
        else:
            raise ValueError(f"Carpeta inválida: {carpeta}")
    
    @staticmethod
    def guardar_archivo_temporal(archivo, upload_folder: str) -> str:
        """Guarda el archivo temporalmente para subirlo a MEGA"""
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(upload_folder, filename)
        archivo.save(filepath)
        
        return filepath
    
    @staticmethod
    def limpiar_archivo_temporal(filepath: str):
        """Elimina el archivo temporal"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Archivo temporal eliminado: {filepath}")
        except Exception as e:
            logger.error(f"Error al eliminar archivo temporal: {e}")
