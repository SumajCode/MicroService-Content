from flask import Blueprint
from controllers.archivo_controller import ArchivoController

# Crear blueprint para las rutas de archivos
archivo_bp = Blueprint('archivos', __name__, url_prefix='/archivos')

# Instanciar el controlador
archivo_controller = ArchivoController()

# Definir rutas
@archivo_bp.route('/recursos/subir', methods=['POST'])
def subir_archivo():
    """Ruta para subir archivos"""
    return archivo_controller.subir_archivo()

@archivo_bp.route('/recursos/<archivo_id>', methods=['PUT'])
def reemplazar_archivo(archivo_id):
    """Ruta para reemplazar un archivo existente"""
    return archivo_controller.reemplazar_archivo(archivo_id)

@archivo_bp.route('/recursos/<archivo_id>', methods=['DELETE'])
def eliminar_archivo(archivo_id):
    """Ruta para eliminar un archivo"""
    return archivo_controller.eliminar_archivo(archivo_id)

@archivo_bp.route('/recursos/usuario/<usuario_id>', methods=['GET'])
def obtener_archivos_usuario(usuario_id):
    """Ruta para obtener todos los archivos de un usuario"""
    return archivo_controller.obtener_archivos_usuario(usuario_id)

# Blueprint para rutas de usuarios
usuario_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuario_bp.route('/recursos/<usuario_id>', methods=['DELETE'])
def eliminar_usuario_completo(usuario_id):
    """Ruta para eliminar todo el contenido de un usuario"""
    return archivo_controller.eliminar_usuario_completo(usuario_id)
