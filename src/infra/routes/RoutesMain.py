from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask import Blueprint
from infra.routes.RoutesContenido import blueprint as blueCont
from infra.routes.RoutesModulo import blueprint as blueMod

def crearApp():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.settings.Config')
    padreBlueprint = Blueprint('apicontenido', __name__, url_prefix='/apicontenido/v1')
    
    @padreBlueprint.route('/')
    def home():
        """
        Root route of the API

        Returns a JSON response with the status of the API

        :return: JSON response with the status of the API
        """
        return jsonify({
            'data': f"{app.config['APP_NAME']+ '-' + app.config['APP_VERSION']} is running", 
            'message' : 'OK', 
            'status' : 200
        })
    
    padreBlueprint.register_blueprint(blueCont)
    padreBlueprint.register_blueprint(blueMod)
    app.register_blueprint(padreBlueprint)
    
    return app
