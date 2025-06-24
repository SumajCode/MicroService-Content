from domain.mongodb.MongoService import ServicioMongoDB
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
            if opciones['todo']:
                self.connColeccion.delete_many(opciones['filtro'])
                return "Lista de datos eliminados correctamente."
            self.connColeccion.delete_one(opciones['filtro'])
            return "Datos eliminados correctamente."
        except Exception as e:
            return f"Hubo un fallo al eliminar los datos: {e}"

    def actualizarDatosEnColeccion(self, opciones: dict):
        try:
            if opciones['todo']:
                self.connColeccion.update_many(opciones['filtro'], {'$set': opciones['datos']})
                return "Lista de datos actualizados correctamente."
            if 'id' in opciones['filtro']:
                opciones['filtro']['_id'] = ObjectId(opciones['filtro'].pop('id'))
            self.connColeccion.update_one(opciones['filtro'], {'$set': opciones['datos']})
            return "Datos actualizados correctamente."
        except Exception as e:
            return f"Hubo un fallo al actualizar los datos: {e}"

    def encontrarDatos(self, opciones: dict):
        try:
            if opciones['todo']:
                datos = list(self.connColeccion.find(opciones['datos'], opciones['proyeccion']))
                for dato in datos:
                    dato['_id'] = str(dato['_id'])
                return {
                    'data':datos,
                    'message': "Lista de datos encontrados."
                }
            datos = self.connColeccion.find_one(opciones['datos'], opciones['proyeccion'])
            print('Datos: ', datos)
            datos['_id'] = str(datos['_id'])
            return {
                'data': datos,
                'message': "Datos encontrados."
            }
        except Exception as e:
            return {
                'data':None,
                'message': f"Hubo un fallo al encontrar los datos: {e}"
            }

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