from flask import Blueprint
from src.controllers.entrega_controller import EntregaController

# Crear blueprint para las rutas de entregas
entrega_bp = Blueprint('entregas', __name__, url_prefix='/entregas')

# Instanciar el controlador
entrega_controller = EntregaController()

# Obtener entregas por tarea y estudiante
@entrega_bp.route('/obtener', methods=['POST'])
def obtener_entregas():
    """Obtener entregas por tarea y estudiante"""
    return entrega_controller.obtener_entregas()

# Crear entrega
@entrega_bp.route('/', methods=['POST'])
def crear_entrega():
    """Crear una nueva entrega"""
    return entrega_controller.crear_entrega()

# Actualizar entrega
@entrega_bp.route('/', methods=['PUT'])
def actualizar_entrega():
    """Actualizar una entrega existente"""
    return entrega_controller.actualizar_entrega()

# Subir archivos para entrega
@entrega_bp.route('/upload', methods=['POST'])
def subir_archivo_entrega():
    """Subir archivos para una entrega"""
    return entrega_controller.subir_archivo_entrega()
