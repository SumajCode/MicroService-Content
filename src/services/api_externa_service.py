import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional, Dict
import logging
import json

logger = logging.getLogger(__name__)

class ApiExternaService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MicroService-Content/1.0'
        })
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def obtener_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Obtiene información de un usuario desde la API externa"""
        try:
            url = f"{self.base_url}{usuario_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Usuario no encontrado: {usuario_id}")
                return None
            else:
                logger.error(f"Error en API externa: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con API externa: {e}")
            # Fallback a datos mock para desarrollo
            return self._obtener_usuario_mock(usuario_id)
    
    def _obtener_usuario_mock(self, usuario_id: str) -> Optional[Dict]:
        """Datos mock para pruebas cuando la API externa no está disponible"""
        usuarios_mock = {
            "u001": {
                "usuario_id": "u001",
                "nombre_usuario": "Carlos Ramírez"
            },
            "u123": {
                "usuario_id": "u123",
                "nombre_usuario": "María González"
            },
            "u999": {
                "usuario_id": "u999",
                "nombre_usuario": "Ana López"
            },
            "u777": {
                "usuario_id": "u777",
                "nombre_usuario": "Pedro Martínez"
            }
        }
        
        usuario = usuarios_mock.get(usuario_id)
        if usuario:
            logger.info(f"Usando datos mock para usuario: {usuario_id}")
        
        return usuario
