from infra.controllers.Controller import Controller
from infra.models.ModuloModel import Modulo
from config.settings import Config

class ModuloController(Controller):
    
    def __init__(self):
        modelo = Modulo()
        self.nombreColeccion = modelo.nombreColeccion
        self.columnas = modelo.opciones['columns']
        super().__init__(self.nombreColeccion)
        
    def obtener(self, request):
        proyeccion = {
            '_id': 1,
            'id_docente': 1,
            'id_materia':1,
            'files':1,
            'structure':1,
        }
        self.get({'request':request, 'proyeccion':proyeccion})

    def crearRegistro(self, request):
        self.post(request)

    def actualizarRegistro(self, request):
        pass

    def eliminarRegistro(self, request):
        pass