from flask import Blueprint
from flask import request

from infra.controllers.ContenidoController import ContenidoController

controlador = ContenidoController()
blueprint = Blueprint('archivo', __name__, url_prefix='/archivo')

@blueprint.route('/eliminar', methods=['DELETE'])
def eliminarArchivo():
    return controlador.eliminarRegistro(request)

@blueprint.route('/listar', methods=['GET', 'POST'])
def obtenerArchivos():
    return controlador.obtener(request)

@blueprint.route('/crear', methods=['POST'])
def crearArchivo():
    return controlador.crearRegistro(request)

@blueprint.route('/editar', methods=['PATCH'])
def editarArchivo():
    return controlador.actualizarRegistro(request)