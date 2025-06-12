from infra.models.CursoModel import Curso
from scripts.execute import Ejecutar

ejecutar = Ejecutar()

@ejecutar.crearColeccion()
def crearColeccionCurso():
    return Curso()
