from pymongo import MongoClient
from config.settings import Config

class ServicioMongoDB:
    def __init__(self):
        self.user = Config.MONGO_USER
        self.password = Config.MONGO_PASSWORD
        self.host = Config.MONGO_HOST
        self.db = Config.MONGO_DB
        self.appname = Config.MONGO_APP_NAME
        self.srv = Config.MONGO_SRV
        self.uri = Config.MONGO_URI
    
    def connection(self):
        params = {
            'host':self.host,
            'username':self.user,
            'password':self.password,
            'appname':self.appname,
        }
        if self.srv:
            return MongoClient(self.uri)
        return MongoClient(**params)

    def connectionDB(self):
        if self.db:
            client = self.connection()
            return client[self.db]
        return 'Revisa las variables de entorno pendejo. xd'
