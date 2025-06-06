from flask import Blueprint
from controllers.tema_controller import TemaController

# Crear blueprint para las rutas de temas
tema_bp = Blueprint('temas', __name__, url_prefix='/temas')

# Instanciar el controlador
tema_controller = TemaController()

# Obtener temas por curso
@tema_bp.route('/obtener', methods=['POST'])
def obtener_temas():
    """Obtener temas por curso"""
    return tema_controller.obtener_temas()

# Crear tema
@tema_bp.route('/', methods=['POST'])
def crear_tema():
    """Crear un nuevo tema"""
    return tema_controller.crear_tema()

# Actualizar tema
@tema_bp.route('/', methods=['PUT'])
def actualizar_tema():
    """Actualizar un tema existente"""
    return tema_controller.actualizar_tema()

# Eliminar tema
@tema_bp.route('/', methods=['DELETE'])
def eliminar_tema():
    """Eliminar un tema"""
    return tema_controller.eliminar_tema()
