from flask import Blueprint
from src.controllers.publicacion_controller import PublicacionController

# Crear blueprint para las rutas de publicaciones
publicacion_bp = Blueprint('publicaciones', __name__, url_prefix='/publicaciones')

# Instanciar el controlador
publicacion_controller = PublicacionController()

# Obtener publicaciones por tema
@publicacion_bp.route('/obtener', methods=['POST'])
def obtener_publicaciones():
    """Obtener publicaciones por tema"""
    return publicacion_controller.obtener_publicaciones()

# Crear publicación
@publicacion_bp.route('/', methods=['POST'])
def crear_publicacion():
    """Crear una nueva publicación"""
    return publicacion_controller.crear_publicacion()

# Actualizar publicación
@publicacion_bp.route('/', methods=['PUT'])
def actualizar_publicacion():
    """Actualizar una publicación existente"""
    return publicacion_controller.actualizar_publicacion()

# Eliminar publicación
@publicacion_bp.route('/', methods=['DELETE'])
def eliminar_publicacion():
    """Eliminar una publicación"""
    return publicacion_controller.eliminar_publicacion()

# Subir archivo para publicación
@publicacion_bp.route('/upload', methods=['POST'])
def subir_archivo_publicacion():
    """Subir archivo para una publicación"""
    return publicacion_controller.subir_archivo_publicacion()
