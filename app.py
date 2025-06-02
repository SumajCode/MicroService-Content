from flask import Flask, jsonify
from routes.archivo_routes import archivo_bp
from config.settings import Config
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    app.config['DEBUG'] = Config.FLASK_DEBUG
    
    # Registrar blueprints
    app.register_blueprint(archivo_bp)
    
    # Ruta de salud
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Servicio funcionando correctamente",
            "data": {
                "service": "MicroService-Content",
                "version": "1.0.0"
            }
        }), 200
    
    # Ruta raíz
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            "status": "success",
            "code": 200,
            "message": "MicroService-Content API",
            "data": {
                "version": "1.0.0",
                "endpoints": {
                    "subir_archivo": "POST /apicontenido/subir",
                    "subir_multiples": "POST /apicontenido/subir-multiples",
                    "obtener_info": "POST /apicontenido/info",
                    "listar_archivos": "POST /apicontenido/listar",
                    "descargar_archivo": "POST /apicontenido/descargar",
                    "descargar_carpeta": "POST /apicontenido/descargar-carpeta",
                    "actualizar_metadatos": "PUT /apicontenido/actualizar",
                    "eliminar_archivo": "DELETE /apicontenido/eliminar",
                    "eliminar_usuario": "DELETE /apicontenido/eliminar-usuario",
                    "health_check": "GET /health"
                }
            }
        }), 200
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "code": 404,
            "message": "Endpoint no encontrado",
            "data": None
        }), 404
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            "status": "error",
            "code": 413,
            "message": "Archivo demasiado grande",
            "data": None
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "status": "error",
            "code": 500,
            "message": "Error interno del servidor",
            "data": None
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )
