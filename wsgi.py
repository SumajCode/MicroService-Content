import sys
import os

# Agregar la carpeta src al path para que se puedan importar los módulos correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
