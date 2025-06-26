from flask import jsonify
from infra.db.Querys import Query
# from domain.mega.MegaService import ServicioMega

class Controller:
    def __init__(self, nombreColeccion):
        self.execQueries = Query(nombreColeccion)
    
    def obtenerRequest(self, request):
        if request.args:
            return request.args.to_dict()
        return request.get_json() if request.is_json else dict(request.form)
    
    def obtenerDatosImportantes(self, request: dict):
        datosEnvio = {}
        if 'data' in request and request['data']:
            datosEnvio['datos'] = request.get('data')
        if 'todo' in request and request['todo']:
            datosEnvio['todo'] = request.get('todo').lower() in ('true', '1', 't', 'yes', 'y')
        if 'filter' in request and request['filter']:
            datosEnvio['filtro'] = request.get('filter')
        if 'files' in request and request['files']:
            datosEnvio['archivos'] = request.files.getlist('files')
            if 'carpeta_nombre' in request and request['carpeta_nombre']:
                datosEnvio['carpeta_nombre'] = request['carpeta_nombre']
            if 'modulo' in request and request['modulo']:
                datosEnvio['modulo'] = request.get('modulo')
        return datosEnvio

    def get(self, opciones=None):
        datos = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
        datos = self.obtenerDatosImportantes(datos)
        datos['proyeccion'] = opciones['proyeccion']
        datosQuery = self.execQueries.encontrarDatos(datos)
        datosEnvio = datosQuery['data']
        if datosEnvio is None:
            datosEnvio = {}
        return jsonify({
            'data':datosEnvio,
            'message': datosQuery['message'],
            'status': 200
        })

    def especialGet(self, opciones: dict):
        respuesta = self.execQueries.encontrarDatosRelacion({
            'coleccion':opciones['coleccion'],
            'id_local':opciones['id_local'],
            'id_relacion': opciones['id_relacion'],
            'as':opciones['as']
        })
        print(respuesta)
        return jsonify({
            'data':respuesta['data'],
            'message':respuesta['message'],
            'status': 200
        })
    
    def post(self, opciones):
        datos = {}
        datosImportantes = {}
        if 'request' in opciones.keys() and opciones['request']:
            datos = self.obtenerRequest(opciones['request'])
            datosImportantes = self.obtenerDatosImportantes(datos)
        claves = datosImportantes['datos'].keys()
        for clave in opciones['rules']:
            if clave not in claves:
                return jsonify({
                    'data': [],
                    'message': f"Falta la columna obligatoria {clave}",
                    'status': 400
                })
        for clave in claves:
            if clave != 'filter' and clave != 'todo':
                if clave not in opciones['columnas'] :
                    return jsonify({
                        'data': [],
                        'message': f"Falta la columna {clave}",
                        'status': 400
                    })
        datos = self.obtenerDatosImportantes(datos)
        datos['id'] = opciones['id']
        message = "Error los datos no son un arreglo."
        if datos['todo']:
            if isinstance(datos['datos'], list):
                message = self.execQueries.insertarEnColeccion(datos)
            return jsonify({
                'data': [],
                'message': message,
                'status': 200
            })
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