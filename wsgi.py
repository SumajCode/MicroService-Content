import os
import sys

# Agregar el directorio actual al PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader

def create_app():
    # Importaciones locales para evitar problemas de importación circular
    from src.config.config import Config
    from src.models.curso_model import CursoModel
    from src.controllers.curso_controller import CursoController
    from src.routes.curso_routes import init_curso_routes
    from src.routes.auth_routes import init_auth_routes
    
    app = Flask(__name__)
    
    # Configuración
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'clave-secreta-desarrollo')
    
    # Configurar CORS
    CORS(app)
    
    # Configurar JWT
    jwt = JWTManager(app)
    
    # Configurar Cloudinary
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    
    # Conectar a MongoDB
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/cursos_db')
        client = MongoClient(mongo_uri)
        # Verificar la conexión
        client.admin.command('ping')
        print("Conexión a MongoDB establecida correctamente")
        db = client.get_database()
    except Exception as e:
        print(f"Error al conectar a MongoDB: {str(e)}")
        db = None
    
    # Inicializar modelos
    curso_model = CursoModel(db)
    
    # Inicializar controladores
    curso_controller = CursoController(curso_model)
    
    # Registrar rutas
    app.register_blueprint(init_auth_routes())
    app.register_blueprint(init_curso_routes(curso_controller))
    
    @app.route('/')
    def index():
        return jsonify({
            "mensaje": "API de Gestión de Cursos",
            "version": "1.0.0",
            "estado": "online"
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Recurso no encontrado"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'False') == 'True'
    )