from flask import Flask, jsonify
from routes.archivo_routes import archivo_bp
from routes.tema_routes import tema_bp
from routes.publicacion_routes import publicacion_bp
from routes.tarea_routes import tarea_bp
from routes.entrega_routes import entrega_bp
from routes.anuncio_routes import anuncio_bp
from config.settings import Config
import logging
from flask_cors import CORS

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Habilitar CORS
    CORS(app)
    
    # Configuración
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    app.config['DEBUG'] = Config.FLASK_DEBUG
    
    # Registrar blueprints - SOLO archivo_bp unificado
    app.register_blueprint(archivo_bp)
    app.register_blueprint(tema_bp)
    app.register_blueprint(publicacion_bp)
    app.register_blueprint(tarea_bp)
    app.register_blueprint(entrega_bp)
    app.register_blueprint(anuncio_bp)
    
    # Ruta de salud
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Servicio funcionando correctamente",
            "data": {
                "service": "MicroService-Content",
                "version": "2.0.0"
            }
        }), 200
                "service": "MicroService-Content",
                "version": "2.0.0"
            }
        }), 200
    
    # Ruta raíz
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            "status": "success",
            "code": 200,
            "message": "MicroService-Content API - Plataforma Educativa (Versión Unificada)",
            "data": {
                "version": "2.0.0",
                "endpoints": {
                    "archivos_contenido": {
                        "subir_archivo": "POST /archivos/contenido/subir",
                        "subir_multiples": "POST /archivos/contenido/subir-multiples",
                        "obtener_info": "POST /archivos/contenido/info",
                        "listar_archivos": "POST /archivos/contenido/listar",
                        "descargar_archivo": "POST /archivos/contenido/descargar",
                        "eliminar_archivo": "DELETE /archivos/contenido/eliminar"
                    },
                    "archivos_educativos": {
                        "subir_publicacion": "POST /archivos/educativo/publicacion/upload",
                        "subir_tarea": "POST /archivos/educativo/tarea/upload",
                        "subir_entrega": "POST /archivos/educativo/entrega/upload",
                        "subir_anuncio": "POST /archivos/educativo/anuncio/upload",
                        "obtener_por_modulo": "POST /archivos/educativo/modulo",
                        "obtener_por_usuario": "POST /archivos/educativo/usuario",
                        "eliminar_archivo": "DELETE /archivos/educativo/eliminar"
                    },
                    "archivos_generales": {
                        "listar_todos": "GET /archivos/listar-todos",
                        "buscar_archivos": "POST /archivos/buscar",
                        "estadisticas": "POST /archivos/estadisticas"
                    },
                    "temas": {
                        "obtener_temas": "POST /temas/obtener",
                        "crear_tema": "POST /temas/",
                        "actualizar_tema": "PUT /temas/",
                        "eliminar_tema": "DELETE /temas/"
                    },
                    "publicaciones": {
                        "obtener_publicaciones": "POST /publicaciones/obtener",
                        "crear_publicacion": "POST /publicaciones/",
                        "actualizar_publicacion": "PUT /publicaciones/",
                        "eliminar_publicacion": "DELETE /publicaciones/"
                    },
                    "tareas": {
                        "obtener_tareas": "POST /tareas/obtener",
                        "crear_tarea": "POST /tareas/",
                        "actualizar_tarea": "PUT /tareas/",
                        "eliminar_tarea": "DELETE /tareas/"
                    },
                    "entregas": {
                        "obtener_entregas": "POST /entregas/obtener",
                        "crear_entrega": "POST /entregas/",
                        "actualizar_entrega": "PUT /entregas/"
                    },
                    "anuncios": {
                        "obtener_anuncios": "POST /anuncios/obtener",
                        "crear_anuncio": "POST /anuncios/",
                        "actualizar_anuncio": "PUT /anuncios/",
                        "eliminar_anuncio": "DELETE /anuncios/"
                    },
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
        logger.error(f"Error interno del servidor: {error}")
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
