from flask import Blueprint
from flask import request

from infra.controllers.ModuloController import ModuloController

controlador = ModuloController()
blueprint = Blueprint('modulo', __name__, url_prefix='/modulo')

@blueprint.route('/eliminar', methods=['DELETE'])
def eliminarModulo():
    return controlador.eliminarRegistro(request)

@blueprint.route('/listar', methods=['GET', 'POST'])
def obtenerModulos():
    return controlador.obtener(request)

@blueprint.route('/contenido', methods=['GET', 'POST'])
def obtenerModulosContenido():
    return controlador.obtenerRelacionContenido()

@blueprint.route('/materias', methods=['GET', 'POST'])
def obtenerModulosMateria():
    return controlador.obtenerModulosPorMateria(request)

@blueprint.route('/crear', methods=['POST'])
def crearModulo():
    return controlador.crearRegistro(request)

@blueprint.route('/editar', methods=['PATCH'])
def editarModulo():
    return controlador.actualizarRegistro(request)