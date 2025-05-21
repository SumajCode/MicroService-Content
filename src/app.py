from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import os
import cloudinary
import cloudinary.uploader

from src.config import Config
from src.models import CursoModel
from src.controllers import CursoController
from src.routes import init_curso_routes, init_auth_routes

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(Config)
    
    # Configurar CORS
    CORS(app)
    
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    jwt = JWTManager(app)
    
    # Configurar Cloudinary
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    
    # Conectar a MongoDB
    try:
        client = MongoClient(Config.MONGO_URI)
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

if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG
    )from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
import os
import cloudinary
import cloudinary.uploader

from src.config import Config
from src.models import CursoModel
from src.controllers import CursoController
from src.routes import init_curso_routes, init_auth_routes

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(Config)
    
    # Configurar CORS
    CORS(app)
    
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    jwt = JWTManager(app)
    
    # Configurar Cloudinary
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    
    # Conectar a MongoDB
    try:
        client = MongoClient(Config.MONGO_URI)
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

if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG
    )