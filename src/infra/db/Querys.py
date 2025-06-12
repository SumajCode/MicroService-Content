from domain.mongodb.MongoService import ServicioMongoDB

class Query:
    def __init__(self):
        mongoService = ServicioMongoDB()
        self.connDB = mongoService.connectionDB()

    def insertarUnicoEnColeccion(self, datos: dict):
        try:
            self.connDB.insert_one(datos)
            return "Datos insertados correctamente."
        except Exception as e:
            return f"Hubo un fallo al insertar los datos: {e}"
    
    def insertarVariosEnColeccion(self, datos: list[dict]):
        try:
            self.connDB.insert_many(datos)
            return "Lista de datos insertados correctamente."
        except Exception as e:
            return f"Hubo un fallo al insertar los datos: {e}"

    def eliminarDatosEnColeccion(self, opciones: dict):
        try:
            if 'todo' in opciones.keys() and opciones['todo']:
                self.connDB.delete_many(opciones['datos'])
                return "Lista de datos eliminados correctamente."
            self.connDB.delete_one(opciones['datos'])
            return "Datos eliminados correctamente."
        except Exception as e:
            return f"Hubo un fallo al insertar los datos: {e}"

    def encontrarDatos(self, opciones: dict):
        try:
            if 'todo' in opciones.keys() and opciones['todo']:
                self.connDB.delete_many(opciones['datos'])
                return "Lista de datos eliminados correctamente."
            self.connDB.delete_one(opciones['datos'])
            return "Datos eliminados correctamente."
        except Exception as e:
            return f"Hubo un fallo al insertar los datos: {e}"

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
        self.connDB.create_collection(datos['nombre_coleccion'], datos['validador'])