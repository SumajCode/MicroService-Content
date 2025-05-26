from flask import Flask, jsonify
from src.routes.archivo_routes import archivo_bp, usuario_bp
from src.config.settings import Config
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
    app.register_blueprint(usuario_bp)
    
    # Ruta de salud
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "MicroService-Content",
            "version": "1.0.0"
        }), 200
    
    # Ruta raíz
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            "message": "MicroService-Content API",
            "version": "1.0.0",
            "endpoints": {
                "subir_archivo": "POST /archivos/subir",
                "reemplazar_archivo": "PUT /archivos/<archivo_id>",
                "eliminar_archivo": "DELETE /archivos/<archivo_id>",
                "obtener_archivos_usuario": "GET /archivos/usuario/<usuario_id>",
                "eliminar_usuario_completo": "DELETE /usuarios/<usuario_id>",
                "health_check": "GET /health"
            }
        }), 200
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint no encontrado"}), 404
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({"error": "Archivo demasiado grande"}), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG
    )
