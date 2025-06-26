from domain.mongodb.MongoService import ServicioMongoDB
from infra.db.MegaQueries import subirArchivos, convertirDictArchivo
from bson import ObjectId
from datetime import datetime

class Query:
    def __init__(self, nombreColeccion):
        mongoService = ServicioMongoDB()
        self.connDB = mongoService.connectionDB()
        self.connColeccion = self.connDB[nombreColeccion]

    def insertarEnColeccion(self, opciones: dict):
        try:
            datos = opciones['datos']
            id = opciones['id']
            if 'files' in datos.keys():
                archivos = list(datos['files'])
                datosArchivos = {'archivos': convertirDictArchivo(archivos)}
                if 'carpeta_nombre' in opciones:
                    datosArchivos['carpeta_nombre'] = opciones['carpeta_nombre']
                if 'modulo' in opciones:
                    datosArchivos['modulo'] = opciones['modulo']
                datos['files'] = subirArchivos(datosArchivos)
            if opciones['todo']:
                for dato in datos:
                    dato[id] = ObjectId()
                    dato['timestamp'] = datetime.utcnow()
                self.connColeccion.insert_many(opciones['datos'])
                return "Lista de datos agregados correctamente."
            datos[id] = ObjectId()
            datos['timestamp'] = datetime.utcnow()
            self.connColeccion.insert_one(opciones['datos'])
            return "Datos agregados correctamente."
        except Exception as e:
            return f"Hubo un fallo al insertar los datos: {e}"

    def eliminarDatosEnColeccion(self, opciones: dict):
        try:
            filtro = self.cambiarAObjectId(opciones['filtro'])
            if opciones['todo']:
                self.connColeccion.delete_many(filtro)
                return "Lista de datos eliminados correctamente."
            self.connColeccion.delete_one(filtro)
            return "Datos eliminados correctamente."
        except Exception as e:
            return f"Hubo un fallo al eliminar los datos: {e}"

    def actualizarDatosEnColeccion(self, opciones: dict):
        try:
            filtro = self.cambiarAObjectId(opciones['filtro'])
            if opciones['todo']:
                self.connColeccion.update_many(filtro, {'$set': opciones['datos']})
                return "Lista de datos actualizados correctamente."
            self.connColeccion.update_one(filtro, {'$set': opciones['datos']})
            return "Datos actualizados correctamente."
        except Exception as e:
            return f"Hubo un fallo al actualizar los datos: {e}"

    def encontrarDatos(self, opciones: dict):
        try:
            filtro = {}
            for clave, valor in opciones.get('filtro', {}).items():
                if isinstance(valor, str) and len(valor) == 24:
                    try:
                        filtro[clave] = ObjectId(valor)
                    except Exception:
                        filtro[clave] = valor
                else:
                    filtro[clave] = valor
            if opciones['todo']:
                datosTemp = list(self.connColeccion.find(filtro, opciones['proyeccion']))
                datosEnvio = []
                for dato in datosTemp:
                    print(dato)
                    datosEnvio.append(self.cambiarAObjectId(dato))
                return {
                    'data':datosEnvio,
                    'message': "Lista de datos encontrados."
                }
            datos = self.connColeccion.find_one(filtro, opciones['proyeccion'])
            datos = self.cambiarAObjectId(datos)
            if len(datos) > 0:
                return {
                    'data': datos,
                    'message': "Datos encontrados."
                }
            return {
                'data': {},
                'message': "No existe un registro con ese id."
            }
        except Exception as e:
            return {
                'data':None,
                'message': f"Hubo un fallo al encontrar los datos: {e}"
            }

    def encontrarDatosRelacion(self, opciones: dict):
        try:
            pipeline = []
            if 'match' in opciones.keys() and 'campo_match' in opciones.keys():
                pipeline.append({
                    '$match': {
                        opciones['campo_match']: opciones['match']
                    }
                })
            pipeline.append({
                '$lookup': {
                    'from': opciones['coleccion'],
                    'localField': opciones['id_local'],
                    'foreignField': opciones['id_relacion'],
                    'as': opciones['as']
                }
            })
            resultados = list(self.connColeccion.aggregate(pipeline))
            return {
                'data': [self.cambiarAObjectId(r) for r in resultados],
                'message': "Módulos con sus contenidos obtenidos correctamente."
            }
        except Exception as e:
            return {
                'data': None,
                'message': f"Error al obtener módulos con contenidos: {e}"
            }

    def cambiarAObjectId(self, dato):
        if isinstance(dato, dict):
            return {
                key: self.cambiarAObjectId(value)
                for key, value in dato.items()
            }
        elif isinstance(dato, list):
            return [self.cambiarAObjectId(item) for item in dato]
        elif isinstance(dato, ObjectId):
            return str(dato)
        else:
            return dato

    def contarRegistros(self, nombreColeccion: str):
        try:
            if nombreColeccion and len(nombreColeccion) > 0:
                return self.connDB[nombreColeccion].estimated_document_count()
        except Exception as e:
            return f"Error encontrado al retornar cantidad de registros: {e}"

    def valorUnico(self, valorUnico: str, indices: list, nombreColeccion: str):
        if nombreColeccion is not None and len(nombreColeccion) > 0 :
            if valorUnico is not None:
                coleccion = self.connDB[nombreColeccion]
                for index in indices:
                    if index[0] == valorUnico:
                        coleccion.create_index([index], unique=True)
                    else:
                        coleccion.create_index([index])
            else:
                self.crearIndice(nombreColeccion, indices)

    def crearIndice(self, nombreColeccion: str, indices: list = None):
        if indices:
            coleccion = self.connDB[nombreColeccion]
            for index in indices:
                coleccion.create_index([index])

    def crearColeccion(self, datos: dict):
        self.connDB.create_collection(datos['nombre_coleccion'], validator=datos['validador'])