import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/microservice_content')
    MEGA_EMAIL = os.getenv('MEGA_EMAIL')
    MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')
    API_USUARIOS_URL = os.getenv('API_USUARIOS_URL', 'https://mock-api-external.local/api/usuarios/')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    PORT = int(os.getenv('PORT', 5000))  # Puerto para Render
    
    # Tipos de contenido permitidos
    TIPOS_CONTENIDO = ['personal', 'educativo']
    
    # Estados de archivo
    ESTADOS_ARCHIVO = ['activo', 'archivado', 'eliminado']
