from infra.db.Collection import CollectionMongo
from domain.mongodb.MongoService import ServicioMongoDB

class Ejecutar():
    def __init__(self):
        """
        Initializes the Ejecutar class by connecting to the database.
        If POSTGRES_ACTIVE is True, it connects to the PostgreSQL database.
        If SQL_ACTIVE is True, it connects to the SQL Server database.
        If both are True, it connects to both databases.
        """
        connexion = ServicioMongoDB()
        self.connMongoDB = connexion.connectionDB()

    def ejecutarConsulta(self, consulta: str):
        """
        Executes a SQL query on the database and returns the results.

        This function takes a SQL query, executes it on the database, and returns the
        results of the query as a list of tuples.

        Args:
            consulta (str): The SQL query to be executed.

        Returns:
            list: A list of tuples containing the results of the query.
        """
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