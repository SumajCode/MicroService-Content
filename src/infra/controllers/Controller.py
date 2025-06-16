from flask import jsonify
from infra.db.Querys import Query
from domain.mega.MegaService import ServicioMega

class Controller:
    def __init__(self, nombreColeccion):
        self.execQueries = Query(nombreColeccion)
    
    def obtenerRequest(request):
        return request.get_json() if request.is_json else request.form()
    
    def obtenerDatosImportantes(request: dict):
        todo = False
        datos = {}
        if 'todo' in request.keys() and request['todo']:
            todo = request['todo'].lower() in ('true', '1', 't', 'yes', 'y')
        if 'data' in request.keys() and request['data']:
            datos = request['data']
        return {'todo': todo, 'datos': datos}

    def get(self, opciones=None):
        datos = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
        datos = self.obtenerDatosImportantes(datos)
        datos['proyeccion'] = opciones['proyeccion']
        datosQuery = self.execQueries.encontrarDatos(datos)
        return jsonify({
            'data':datosQuery['data'] ,
            'message': datosQuery['message'],
            'status': 200
        })
    
    def post(self, opciones):
        datos = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
        datos = self.obtenerDatosImportantes(datos)
        return jsonify({
            'data': [],
            'message': self.execQueries.insertarEnColeccion(datos),
            'status': 200
        })
    
    def put(self, opciones):
        datos = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
        datos = self.obtenerDatosImportantes(datos)
        return jsonify({
            'data': [],
            'message': self.execQueries.actualizarDatosEnColeccion(datos),
            'status': 200
        })
    
    def patch(self, opciones):
        datos = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
        datos = self.obtenerDatosImportantes(datos)
        return jsonify({
            'data': [],
            'message': self.execQueries.actualizarDatosEnColeccion(datos),
            'status': 200
        })
    
    def delete(self, opciones):
        datos = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
        datos = self.obtenerDatosImportantes(datos)
        return jsonify({
            'data': [],
            'message': self.execQueries.eliminarDatosEnColeccion(datos),
            'status': 200
        })
