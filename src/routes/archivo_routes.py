from flask import Blueprint
from controllers.archivo_controller import ArchivoController

# Crear blueprint para las rutas de archivos
archivo_bp = Blueprint('archivos', __name__, url_prefix='/apicontenido')

# Instanciar el controlador
archivo_controller = ArchivoController()

# 1. Subir un archivo a una carpeta específica
@archivo_bp.route('/apicontenido/subir', methods=['POST'])
def subir_archivo():
    """Subir un archivo a una carpeta específica"""
    return archivo_controller.subir_archivo()

# 2. Subir múltiples archivos a una carpeta específica
@archivo_bp.route('/apicontenido/subir-multiples', methods=['POST'])
def subir_multiples_archivos():
    """Subir múltiples archivos a una carpeta específica"""
    return archivo_controller.subir_multiples_archivos()

# 3. Obtener información de un archivo (devuelve el link)
@archivo_bp.route('/apicontenido/info', methods=['POST'])
def obtener_info_archivo():
    """Obtener información de un archivo"""
    return archivo_controller.obtener_info_archivo()

# 4. Listar todos los archivos de un usuario por carpeta
@archivo_bp.route('/apicontenido/listar', methods=['POST'])
def listar_archivos_usuario_carpeta():
    """Listar archivos de un usuario por carpeta"""
    return archivo_controller.listar_archivos_usuario_carpeta()

# 5. Descargar un archivo
@archivo_bp.route('/apicontenido/descargar', methods=['POST'])
def descargar_archivo():
    """Descargar un archivo específico"""
    return archivo_controller.descargar_archivo()

# 6. Descargar todos los archivos de la carpeta de un usuario como .zip
@archivo_bp.route('/apicontenido/descargar-carpeta', methods=['POST'])
def descargar_carpeta_zip():
    """Descargar carpeta completa como ZIP"""
    return archivo_controller.descargar_carpeta_zip()

# 7. Actualizar metadatos del archivo
@archivo_bp.route('/apicontenido/actualizar', methods=['PUT'])
def actualizar_metadatos():
    """Actualizar metadatos de un archivo"""
    return archivo_controller.actualizar_metadatos()

# 8. Eliminar un archivo
@archivo_bp.route('/apicontenido/eliminar', methods=['DELETE'])
def eliminar_archivo():
    """Eliminar un archivo específico"""
    return archivo_controller.eliminar_archivo()

# 9. Eliminar todos los archivos y la carpeta de un usuario
@archivo_bp.route('/apicontenido/eliminar-usuario', methods=['DELETE'])
def eliminar_usuario_completo():
    """Eliminar todo el contenido de un usuario"""
    return archivo_controller.eliminar_usuario_completo()
