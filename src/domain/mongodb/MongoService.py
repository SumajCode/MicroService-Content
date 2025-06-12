from pymongo import MongoClient
from config.settings import Config

class ServicioMongoDB:
    def __init__(self):
        self.user = Config.MONGO_USER
        self.password = Config.MONGO_PASSWORD
        self.host = Config.MONGO_HOST
        self.replic = Config.MONGO_REPLIC
        self.auth = Config.MONGO_AUTH
        self.port = Config.MONGO_PORT
        self.db = Config.MONGO_DB
    
    def connection(self):
        params = {
            'host':[f"{self.host}:{self.port}"]*3,
            'username':self.user,
            'password':self.password
        }
        if self.auth:
            params['authSource'] = self.auth
        if self.replic:
            params['replicaSet'] = self.replic
        return MongoClient(**params)

    def connectionDB(self):
        if self.db:
            with self.connection as client:
                return client[self.db]
        return 'Revisa las variables de entorno pendejo. xd'
