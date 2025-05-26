import os
from app import create_app

# Crear la aplicación para el servidor WSGI
application = create_app()

if __name__ == "__main__":
    application.run()
