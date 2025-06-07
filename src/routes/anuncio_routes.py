from flask import Blueprint
from src.controllers.anuncio_controller import AnuncioController

# Crear blueprint para las rutas de anuncios
anuncio_bp = Blueprint('anuncios', __name__, url_prefix='/anuncios')

# Instanciar el controlador
anuncio_controller = AnuncioController()

# Obtener anuncios por curso
@anuncio_bp.route('/obtener', methods=['POST'])
def obtener_anuncios():
    """Obtener anuncios por curso"""
    return anuncio_controller.obtener_anuncios()

# Crear anuncio
@anuncio_bp.route('/', methods=['POST'])
def crear_anuncio():
    """Crear un nuevo anuncio"""
    return anuncio_controller.crear_anuncio()

# Actualizar anuncio
@anuncio_bp.route('/', methods=['PUT'])
def actualizar_anuncio():
    """Actualizar un anuncio existente"""
    return anuncio_controller.actualizar_anuncio()

# Eliminar anuncio
@anuncio_bp.route('/', methods=['DELETE'])
def eliminar_anuncio():
    """Eliminar un anuncio"""
    return anuncio_controller.eliminar_anuncio()

# Subir archivo para anuncio
@anuncio_bp.route('/upload', methods=['POST'])
def subir_archivo_anuncio():
    """Subir archivo para un anuncio"""
    return anuncio_controller.subir_archivo_anuncio()
