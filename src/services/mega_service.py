from mega import Mega
from typing import Optional, Dict
import logging
import os
import tempfile

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
    
    def subir_archivo(self, archivo_path: str, carpeta_destino: str, nombre_archivo: str) -> Optional[Dict]:
        """Sube un archivo a MEGA"""
        try:
            # Crear carpeta si no existe
            self.crear_carpeta(carpeta_destino)
            
            # Encontrar la carpeta destino - CORREGIDO
            carpetas = self.m.get_files()
            carpeta_id = None
            
            # Dividir la ruta para encontrar la estructura completa
            partes_ruta = [p for p in carpeta_destino.split('/') if p]
            
            # Buscar la carpeta siguiendo la estructura jerárquica
            carpeta_actual = None
            for i, parte in enumerate(partes_ruta):
                for file_id, file_info in carpetas.items():
                    if (file_info['a'] and 
                        file_info['a'].get('n') == parte and 
                        file_info['t'] == 1):  # t=1 indica carpeta
                        # Verificar que esté en el nivel correcto de la jerarquía
                        if (carpeta_actual is None and file_info.get('p') is None) or \
                           (carpeta_actual is not None and file_info.get('p') == carpeta_actual):
                            carpeta_actual = file_id
                            if i == len(partes_ruta) - 1:  # Es la última carpeta
                                carpeta_id = file_id
                            break
            
            # Si no se encontró la carpeta, usar la última carpeta creada
            if carpeta_id is None:
                # Buscar la carpeta del usuario (última parte de la ruta)
                usuario_id = partes_ruta[-1] if partes_ruta else None
                if usuario_id:
                    for file_id, file_info in carpetas.items():
                        if (file_info['a'] and 
                            file_info['a'].get('n') == usuario_id and 
                            file_info['t'] == 1):
                            carpeta_id = file_id
                            break
            
            # Validaciones previas antes de subir
            if not carpeta_id:
                logger.error(f"No se encontró carpeta destino válida para la ruta: {carpeta_destino}")
                return None

            if not os.path.exists(archivo_path):
                logger.error(f"Archivo temporal no encontrado: {archivo_path}")
                return None

            # Logs informativos antes de subir
            logger.info(f"Subiendo archivo a MEGA...")
            logger.info(f"Ruta temporal del archivo: {archivo_path}")
            logger.info(f"ID de carpeta destino en MEGA: {carpeta_id}")
            logger.info(f"Nombre del archivo a subir: {nombre_archivo}")

            # Subir archivo
            file_handle = self.m.upload(archivo_path, carpeta_id, nombre_archivo)

            # Obtener link público
            link = self.m.get_upload_link(file_handle)
            
            logger.info(f"Archivo subido exitosamente: {nombre_archivo} en carpeta: {carpeta_destino}")
            return {
                "link": link,
                "node_id": file_handle
            }
            
        except Exception as e:
            logger.error(f"Error al subir archivo: {e}")
            return None
    
    def descargar_archivo(self, node_id: str) -> Optional[str]:
        """Descarga un archivo de MEGA y retorna la ruta temporal"""
        try:
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp()
            
            # Descargar archivo
            archivo_descargado = self.m.download(node_id, temp_dir)
            
            logger.info(f"Archivo descargado: {archivo_descargado}")
            return archivo_descargado
            
        except Exception as e:
            logger.error(f"Error al descargar archivo: {e}")
            return None
    
    def eliminar_archivo(self, node_id: str) -> bool:
        """Elimina un archivo de MEGA usando su node_id"""
        try:
            self.m.delete(node_id)
            logger.info(f"Archivo eliminado: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False
    
    def mover_archivo(self, node_id: str, nueva_ruta: str) -> bool:
        """Mueve un archivo a una nueva carpeta"""
        try:
            # Crear carpeta destino si no existe
            self.crear_carpeta(nueva_ruta)
            
            # Encontrar la carpeta destino - CORREGIDO
            carpetas = self.m.get_files()
            carpeta_destino_id = None
            
            # Dividir la ruta para encontrar la estructura completa
            partes_ruta = [p for p in nueva_ruta.split('/') if p]
            
            # Buscar la carpeta siguiendo la estructura jerárquica
            carpeta_actual = None
            for i, parte in enumerate(partes_ruta):
                for file_id, file_info in carpetas.items():
                    if (file_info['a'] and 
                        file_info['a'].get('n') == parte and 
                        file_info['t'] == 1):
                        if (carpeta_actual is None and file_info.get('p') is None) or \
                           (carpeta_actual is not None and file_info.get('p') == carpeta_actual):
                            carpeta_actual = file_id
                            if i == len(partes_ruta) - 1:
                                carpeta_destino_id = file_id
                            break
            
            if carpeta_destino_id:
                # Mover archivo
                self.m.move(node_id, carpeta_destino_id)
                logger.info(f"Archivo movido a: {nueva_ruta}")
                return True
            else:
                logger.error(f"No se pudo encontrar la carpeta destino: {nueva_ruta}")
                return False
            
        except Exception as e:
            logger.error(f"Error al mover archivo: {e}")
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
