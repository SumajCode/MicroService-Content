from infra.controllers.Controller import Controller
from infra.models.ContenidoModel import Contenido
from datetime import datetime

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
        datos = request.get_json()
        try:
            if 'time_deliver' in datos['data']:
                fechaString = datos['data']['time_deliver']
                if "T" in fechaString:
                    fecha = datetime.fromisoformat(fechaString.replace("Z", "+00:00"))
                else:
                    fecha = datetime.strptime(fechaString, "%Y-%m-%d")
                datos["data"]["time_deliver"] = fecha
        except Exception as excep:
            print(f'Hubo un error con la fecha: {excep}')
        if "files" in datos["data"]:
            datos["data"]["files"] = [f for f in datos["data"]["files"] if f]

        class RequestWrapper:
            def __init__(self, json_data):
                self._json_data = json_data
                self.args = {}
                self.form = {}
                self.is_json = True

            def get_json(self):
                return self._json_data

        return self.post({
            'request': RequestWrapper(datos),
            'id': self.columnas[0],
            'rules': self.columnas[1:4],
            'columnas': self.columnas})

    def actualizarRegistro(self, request):
        return self.patch({'request': request})

    def eliminarRegistro(self, request):
        return self.delete({'request': request})