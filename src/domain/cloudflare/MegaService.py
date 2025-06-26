from mega import Mega
from config.settings import Config
from domain.mongodb.MongoService import ServicioMongoDB

class ServicioMega:
    def __init__(self):
        self.conn = Mega()
        self.client = self.conn.login(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.client = None
        self.tempPath = Config.TEMP_PATH
        self.mongo = ServicioMongoDB().connectionDB()
        self.contenido = self.mongo['contenido']

    # def connection(self):
    #     return self.conn.login(self.email, self.password)