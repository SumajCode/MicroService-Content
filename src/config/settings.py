import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_DB = os.getenv('MONGO_DB')
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST')
    MONGO_PORT = os.getenv('MONGO_PORT')
    MONGO_APP_NAME = os.getenv('MONGO_APP_NAME')
    MEGA_EMAIL = os.getenv('MEGA_EMAIL')
    MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')
    API_USUARIOS_URL = os.getenv('API_USUARIOS_URL')
    FLASK_ENV = os.getenv('FLASK_ENV')
    PORT = os.getenv('PORT')
    
    # Tipos de contenido permitidos
    TIPOS_CONTENIDO = ['personal', 'educativo']
    
    # Estados de archivo
    ESTADOS_ARCHIVO = ['activo', 'archivado', 'eliminado']
