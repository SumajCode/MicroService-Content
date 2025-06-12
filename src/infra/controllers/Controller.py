from flask import jsonify
from src.services.mongo_service import MongoService
from src.services.mega_service import MegaService

class Controller:
    def __init__(self):
        pass
    
    def obtenerRequest(self, request):
        return request.get_json() if request.is_json else request.form()
    
    def get(self, request):
        datos = self.obtenerRequest(request)
        return
    
    def post(self, request):
        datos = self.obtenerRequest(request)
        return
    
    def put(self, request):
        datos = self.obtenerRequest(request)
        return
    
    def patch(self, request):
        datos = self.obtenerRequest(request)
        return
    
    def delete(self, request):
        datos = self.obtenerRequest(request)
        return
