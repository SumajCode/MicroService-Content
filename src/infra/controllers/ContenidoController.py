from infra.controllers.Controller import Controller
from infra.models.ContenidoModel import Contenido

class ContenidoController(Controller):
    
    def __init__(self):
        modelo = Contenido()
        self.nombreColeccion = modelo.nombreColeccion
        self.columnas = modelo.opciones['columns']
        super().__init__(self.nombreColeccion)
        
    def obtener(self, request):
        return self.get({
            'request':request, 
            'proyeccion':{}})

    def crearRegistro(self, request):
        return self.post({
            'request': request,
            'id': self.columnas[0],
            'rules': self.columnas[1:4],
            'columnas': self.columnas})

    def actualizarRegistro(self, request):
        return self.patch({'request': request})

    def eliminarRegistro(self, request):
        return self.delete({'request': request})