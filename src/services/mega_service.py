from mega import Mega
from typing import Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)

class MegaService:
    def __init__(self, email: str, password: str):
        self.mega = Mega()
        self.email = email
        self.password = password
        self.m = None
        self._login()
    
    def _login(self):
        """Inicia sesión en MEGA"""
        try:
            self.m = self.mega.login(self.email, self.password)
            logger.info("Login exitoso en MEGA")
        except Exception as e:
            logger.error(f"Error al hacer login en MEGA: {e}")
            raise
    
    def crear_carpeta(self, ruta: str) -> bool:
        """Crea una carpeta en MEGA si no existe"""
        try:
            # Dividir la ruta en partes
            partes = [p for p in ruta.split('/') if p]
            carpeta_actual = None
            
            for parte in partes:
                carpetas = self.m.get_files()
                carpeta_encontrada = None
                
                # Buscar si la carpeta ya existe
                for file_id, file_info in carpetas.items():
                    if (file_info['a'] and 
                        file_info['a'].get('n') == parte and 
                        file_info['t'] == 1):  # t=1 indica carpeta
                        if carpeta_actual is None or file_info['p'] == carpeta_actual:
                            carpeta_encontrada = file_id
                            break
                
                if carpeta_encontrada:
                    carpeta_actual = carpeta_encontrada
                else:
                    # Crear la carpeta
                    carpeta_actual = self.m.create_folder(parte, carpeta_actual)
                    logger.info(f"Carpeta creada: {parte}")
            
            return True
        except Exception as e:
            logger.error(f"Error al crear carpeta {ruta}: {e}")
            return False
    
    def subir_archivo(self, archivo_path: str, carpeta_destino: str, nombre_archivo: str) -> Optional[str]:
        """Sube un archivo a MEGA"""
        try:
            # Crear carpeta si no existe
            self.crear_carpeta(carpeta_destino)
            
            # Encontrar la carpeta destino
            carpetas = self.m.get_files()
            carpeta_id = None
            
            for file_id, file_info in carpetas.items():
                if (file_info['a'] and 
                    file_info['a'].get('n') == carpeta_destino.split('/')[-2] and 
                    file_info['t'] == 1):
                    carpeta_id = file_id
                    break
            
            # Subir archivo
            file_handle = self.m.upload(archivo_path, carpeta_id, nombre_archivo)
            
            # Obtener link público
            link = self.m.get_upload_link(file_handle)
            logger.info(f"Archivo subido exitosamente: {nombre_archivo}")
            return link
            
        except Exception as e:
            logger.error(f"Error al subir archivo: {e}")
            return None
    
    def eliminar_archivo(self, ruta_archivo: str) -> bool:
        """Elimina un archivo de MEGA"""
        try:
            archivos = self.m.get_files()
            
            for file_id, file_info in archivos.items():
                if (file_info['a'] and 
                    file_info['a'].get('n') in ruta_archivo):
                    self.m.delete(file_id)
                    logger.info(f"Archivo eliminado: {ruta_archivo}")
                    return True
            
            logger.warning(f"Archivo no encontrado: {ruta_archivo}")
            return False
            
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False
    
    def eliminar_carpeta_usuario(self, usuario_id: str) -> bool:
        """Elimina todas las carpetas de un usuario"""
        try:
            carpetas_usuario = [
                f"Contenido Personal/{usuario_id}",
                f"Contenido Educativo/{usuario_id}"
            ]
            
            for carpeta in carpetas_usuario:
                self._eliminar_carpeta_recursiva(carpeta)
            
            logger.info(f"Carpetas del usuario {usuario_id} eliminadas")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar carpetas del usuario: {e}")
            return False
    
    def _eliminar_carpeta_recursiva(self, ruta_carpeta: str):
        """Elimina una carpeta y todo su contenido"""
        try:
            archivos = self.m.get_files()
            
            for file_id, file_info in archivos.items():
                if (file_info['a'] and 
                    ruta_carpeta in str(file_info.get('a', {}).get('n', ''))):
                    self.m.delete(file_id)
                    
        except Exception as e:
            logger.error(f"Error al eliminar carpeta recursiva: {e}")
