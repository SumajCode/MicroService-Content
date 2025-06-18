import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def getBoolEnv(varName, default=False):
        """
        Retrieve a boolean environment variable.

        Args:
            varName (str): The name of the environment variable.
            default (bool): The default value to return if the environment variable is not set.

        Returns:
            bool: True if the environment variable is set to a 
                  truthy value ('true', '1', 't', 'yes', 'y'), otherwise False.
        """

        val = os.getenv(str(varName), str(default))
        return val.lower() in ('true', '1', 't', 'yes', 'y')
    
    APP_NAME = os.getenv('APP_NAME')
    APP_VERSION = os.getenv('APP_VERSION')
    HOST = os.getenv('HOST')
    PORT_API = os.getenv('PORT_API')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = getBoolEnv('DEBUG')
    TESTING = getBoolEnv('TESTING')

    MONGO_DB = os.getenv('MONGO_DB')
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST')
    MONGO_PORT = os.getenv('MONGO_PORT')
    MONGO_APP_NAME = os.getenv('MONGO_APP_NAME')
    MONGO_SRV = os.getenv('MONGO_SRV')
    MONGO_URI = os.getenv('MONGO_URI')
    MEGA_EMAIL = os.getenv('MEGA_EMAIL')
    MEGA_PASSWORD = os.getenv('MEGA_PASSWORD')
    API_USUARIOS_URL = os.getenv('API_USUARIOS_URL')
    FLASK_ENV = os.getenv('FLASK_ENV')
    PORT = os.getenv('PORT')
    
    # Tipos de contenido permitidos
    TIPOS_CONTENIDO = ['personal', 'educativo']
    
    # Estados de archivo
    ESTADOS_ARCHIVO = ['activo', 'archivado', 'eliminado']
