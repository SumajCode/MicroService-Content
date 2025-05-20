from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient

from config import Config
from models import Curso
from api import init_cursos_routes
from api.auth import init_auth_routes

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(Config)
    
    # Configurar CORS
    CORS(app)
    
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    jwt = JWTManager(app)
    
    # Conectar a MongoDB
    client = MongoClient(Config.MONGO_URI)
    db = client.get_database()
    
    # Inicializar modelos
    curso_model = Curso(db)
    
    # Registrar rutas
    app.register_blueprint(init_auth_routes())
    app.register_blueprint(init_cursos_routes(curso_model))
    
    @app.route('/')
    def index():
        return jsonify({
            "mensaje": "API de Gestión de Cursos - v1",
            "estado": "online"
        })
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG
    )