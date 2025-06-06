from flask import Blueprint
from controllers.tarea_controller import TareaController

# Crear blueprint para las rutas de tareas
tarea_bp = Blueprint('tareas', __name__, url_prefix='/tareas')

# Instanciar el controlador
tarea_controller = TareaController()

# Obtener tareas por tema
@tarea_bp.route('/obtener', methods=['POST'])
def obtener_tareas():
    """Obtener tareas por tema"""
    return tarea_controller.obtener_tareas()

# Crear tarea
@tarea_bp.route('/', methods=['POST'])
def crear_tarea():
    """Crear una nueva tarea"""
    return tarea_controller.crear_tarea()

# Actualizar tarea
@tarea_bp.route('/', methods=['PUT'])
def actualizar_tarea():
    """Actualizar una tarea existente"""
    return tarea_controller.actualizar_tarea()

# Eliminar tarea
@tarea_bp.route('/', methods=['DELETE'])
def eliminar_tarea():
    """Eliminar una tarea"""
    return tarea_controller.eliminar_tarea()

# Subir archivo para tarea
@tarea_bp.route('/upload', methods=['POST'])
def subir_archivo_tarea():
    """Subir archivo para una tarea"""
    return tarea_controller.subir_archivo_tarea()
