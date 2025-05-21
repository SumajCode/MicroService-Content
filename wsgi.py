import os
import sys

# Agregar el directorio actual al PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import cloudinary
import cloudinary.uploader

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar CORS
CORS(app)

# Configurar JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'clave-secreta-desarrollo')
jwt = JWTManager(app)

# Configurar Cloudinary (solo si las variables de entorno están disponibles)
if os.getenv('CLOUDINARY_CLOUD_NAME'):
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

# Ruta principal para el health check
@app.route('/')
def index():
    return jsonify({
        "mensaje": "API de Gestión de Cursos",
        "version": "1.0.0",
        "estado": "online"
    })

# Ruta de health check específica
@app.route('/health')
def health():
    return jsonify({
        "status": "ok"
    })

# Manejadores de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Inicializar las rutas y modelos solo si la conexión a MongoDB está disponible
try:
    from pymongo import MongoClient
    from src.models.curso_model import CursoModel
    from src.controllers.curso_controller import CursoController
    from src.routes.curso_routes import init_curso_routes
    from src.routes.auth_routes import init_auth_routes
    
    # Conectar a MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/cursos_db')
    client = MongoClient(mongo_uri)
    # Verificar la conexión
    client.admin.command('ping')
    print("Conexión a MongoDB establecida correctamente")
    db = client.get_database()
    
    # Inicializar modelos
    curso_model = CursoModel(db)
    
    # Inicializar controladores
    curso_controller = CursoController(curso_model)
    
    # Registrar rutas
    app.register_blueprint(init_auth_routes())
    app.register_blueprint(init_curso_routes(curso_controller))
    
except Exception as e:
    print(f"Error al inicializar la aplicación completa: {str(e)}")
    print("La aplicación se iniciará en modo limitado (solo health check)")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 10000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host="0.0.0.0", port=port, debug=debug)