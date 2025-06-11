import pytest
import sys
import os
import mongomock
import unittest.mock as mock

# Agregar el directorio src al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import create_app

# Mock para MongoClient
@pytest.fixture(autouse=True)
def mock_mongo_client():
    """Mock para MongoClient que evita conexiones reales a MongoDB durante los tests"""
    with mock.patch('pymongo.MongoClient', mongomock.MongoClient):
        yield

# Mock para MegaService
@pytest.fixture(autouse=True)
def mock_mega_service():
    """Mock para MegaService que evita conexiones reales a MEGA durante los tests"""
    with mock.patch('src.services.mega_service.MegaService') as mock_mega:
        # Configurar comportamiento del mock si es necesario
        instance = mock_mega.return_value
        instance.crear_carpeta.return_value = True
        instance.subir_archivo.return_value = {"link": "https://example.com/file", "node_id": "123456"}
        instance.descargar_archivo.return_value = "/tmp/test_file.txt"
        instance.eliminar_archivo.return_value = True
        yield mock_mega

@pytest.fixture
def app():
    """Crear una instancia de la aplicación para testing"""
    app = create_app(testing=True)
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    })
    
    return app

@pytest.fixture
def client(app):
    """Crear un cliente de test para la aplicación"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Crear un runner para comandos CLI"""
    return app.test_cli_runner()
