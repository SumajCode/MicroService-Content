from infra.models.ModuloModel import Modulo
from infra.models.ContenidoModel import Contenido
from scripts.execute import Ejecutar

ejecutar = Ejecutar()

@ejecutar.crearColeccion()
def crearColeccionModulo():
    return Modulo()

@ejecutar.crearColeccion()
def crearColeccionContenido():
    return Contenido()