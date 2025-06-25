from infra.controllers.Controller import Controller
from infra.models.ModuloModel import Modulo
from flask import jsonify

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
            'title': 1,
            'desciption': 1,
            'image': 1,
        }
        return self.get({
            'request':request, 
            'proyeccion':proyeccion})

    def obtenerRelacionContenido(self, request):
        try:
            respuesta = self.obtenerRelacionContenido({
            'colecion':self.nombreColeccion,
            'id_local':self.columnas[0],
            'id_relacion': self.columnas[0],
            'as':'contenido'
            })
            return jsonify({
                'data':respuesta['data'],
                'message':respuesta['message'],
                'status': 200
            })
        except:
            return jsonify({
                'data':{},
                'message':'Hubo un erro en la recoleccion de datos.',
                'status': 500
            })

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