from flask import Blueprint
from src.controllers.archivo_educativo_controller import ArchivoEducativoController

# Crear blueprint para las rutas de archivos educativos
archivo_educativo_bp = Blueprint('archivos_educativos', __name__, url_prefix='/archivos')

# Instanciar el controlador
archivo_educativo_controller = ArchivoEducativoController()

# Obtener archivos por usuario
@archivo_educativo_bp.route('/usuario', methods=['POST'])
def obtener_archivos_usuario():
    """Obtener archivos por usuario"""
    return archivo_educativo_controller.obtener_archivos_usuario()

# Obtener archivos por módulo
@archivo_educativo_bp.route('/modulo', methods=['POST'])
def obtener_archivos_modulo():
    """Obtener archivos por módulo"""
    return archivo_educativo_controller.obtener_archivos_modulo()

# Listar todos los archivos
@archivo_educativo_bp.route('/', methods=['GET'])
def listar_todos_archivos():
    """Listar todos los archivos educativos"""
    return archivo_educativo_controller.listar_todos_archivos()

# Eliminar archivo
@archivo_educativo_bp.route('/', methods=['DELETE'])
def eliminar_archivo():
    """Eliminar un archivo educativo"""
    return archivo_educativo_controller.eliminar_archivo()

# Registrar archivo manualmente
@archivo_educativo_bp.route('/', methods=['POST'])
def registrar_archivo():
    """Registrar un archivo manualmente"""
    return archivo_educativo_controller.registrar_archivo()
