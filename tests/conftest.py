import pytest
import sys
import os

# Agregar el directorio src al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import create_app

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
