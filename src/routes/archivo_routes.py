from flask import Blueprint
from src.controllers.archivo_controller import ArchivoController

# Crear blueprint unificado para todas las rutas de archivos
archivo_bp = Blueprint('archivos', __name__, url_prefix='/archivos')

# Instanciar el controlador
archivo_controller = ArchivoController()

# ==================== ARCHIVOS DE CONTENIDO ====================

# 1. Subir un archivo a una carpeta específica (Contenido Personal/Educativo)
@archivo_bp.route('/contenido/subir', methods=['POST'])
def subir_archivo_contenido():
    """Subir un archivo a carpeta de contenido"""
    return archivo_controller.subir_archivo_contenido()

# 2. Subir múltiples archivos a una carpeta específica
@archivo_bp.route('/contenido/subir-multiples', methods=['POST'])
def subir_multiples_archivos_contenido():
    """Subir múltiples archivos a carpeta de contenido"""
    return archivo_controller.subir_multiples_archivos_contenido()

# 3. Obtener información de un archivo de contenido
@archivo_bp.route('/contenido/info', methods=['POST'])
def obtener_info_archivo_contenido():
    """Obtener información de un archivo de contenido"""
    return archivo_controller.obtener_info_archivo_contenido()

# 4. Listar archivos de contenido por carpeta
@archivo_bp.route('/contenido/listar', methods=['POST'])
def listar_archivos_contenido():
    """Listar archivos de contenido por carpeta"""
    return archivo_controller.listar_archivos_contenido()

# 5. Descargar un archivo de contenido
@archivo_bp.route('/contenido/descargar', methods=['POST'])
def descargar_archivo_contenido():
    """Descargar un archivo de contenido"""
    return archivo_controller.descargar_archivo_contenido()

# 6. Eliminar un archivo de contenido
@archivo_bp.route('/contenido/eliminar', methods=['DELETE'])
def eliminar_archivo_contenido():
    """Eliminar un archivo de contenido"""
    return archivo_controller.eliminar_archivo_contenido()

# ==================== ARCHIVOS EDUCATIVOS ====================

# 7. Subir archivos para publicación
@archivo_bp.route('/educativo/publicacion/upload', methods=['POST'])
def subir_archivo_publicacion():
    """Subir archivos para una publicación"""
    return archivo_controller.subir_archivo_publicacion()

# 8. Subir archivos para tarea
@archivo_bp.route('/educativo/tarea/upload', methods=['POST'])
def subir_archivo_tarea():
    """Subir archivos para una tarea"""
    return archivo_controller.subir_archivo_tarea()

# 9. Subir archivos para entrega
@archivo_bp.route('/educativo/entrega/upload', methods=['POST'])
def subir_archivo_entrega():
    """Subir archivos para una entrega"""
    return archivo_controller.subir_archivo_entrega()

# 10. Subir archivos para anuncio
@archivo_bp.route('/educativo/anuncio/upload', methods=['POST'])
def subir_archivo_anuncio():
    """Subir archivos para un anuncio"""
    return archivo_controller.subir_archivo_anuncio()

# 11. Obtener archivos por módulo educativo
@archivo_bp.route('/educativo/modulo', methods=['POST'])
def obtener_archivos_modulo():
    """Obtener archivos por módulo educativo"""
    return archivo_controller.obtener_archivos_modulo()

# 12. Obtener archivos por usuario educativo
@archivo_bp.route('/educativo/usuario', methods=['POST'])
def obtener_archivos_usuario_educativo():
    """Obtener archivos educativos por usuario"""
    return archivo_controller.obtener_archivos_usuario_educativo()

# 13. Eliminar archivo educativo
@archivo_bp.route('/educativo/eliminar', methods=['DELETE'])
def eliminar_archivo_educativo():
    """Eliminar un archivo educativo"""
    return archivo_controller.eliminar_archivo_educativo()

# ==================== ENDPOINTS GENERALES ====================

# 14. Listar todos los archivos (educativos y contenido)
@archivo_bp.route('/listar-todos', methods=['GET'])
def listar_todos_archivos():
    """Listar todos los archivos del sistema"""
    return archivo_controller.listar_todos_archivos()

# 15. Buscar archivos
@archivo_bp.route('/buscar', methods=['POST'])
def buscar_archivos():
    """Buscar archivos por criterios"""
    return archivo_controller.buscar_archivos()

# 16. Obtener estadísticas de archivos
@archivo_bp.route('/estadisticas', methods=['POST'])
def obtener_estadisticas_archivos():
    """Obtener estadísticas de archivos por usuario"""
    return archivo_controller.obtener_estadisticas_archivos()
