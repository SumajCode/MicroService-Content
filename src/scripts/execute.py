from infra.db.Collection import CollectionMongo
from domain.mongodb.MongoService import ServicioMongoDB

class Ejecutar():
    def __init__(self):
        connexion = ServicioMongoDB()
        self.connMongoDB = connexion.connectionDB()

    def ejecutarConsulta(self, consulta: str):
        conn = self.connMongoDB
        return conn
    
    def crearTabla(self):
        def nuevaMigracion(model: CollectionMongo):
            modelo = model()
            print("En espera de la creacion de la Coleccion...")
            nombresColecciones = self.connMongoDB().list_collection_names()
            if modelo.nombreColeccion not in nombresColecciones:
                print(modelo.crearColeccion())
                return "Creacion de Coleccion exitosa."
            print(f"La Coleccion {modelo.nombreColeccion} ya existe.")
            return "La Coleccion ya existe."
        return nuevaMigracion