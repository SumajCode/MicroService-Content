from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

def init_auth_routes():
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        """
        Endpoint para autenticación de usuarios
        """
        try:
            # En un entorno real, aquí verificaríamos las credenciales contra una base de datos
            # Para este ejemplo, simplemente generamos tokens según el rol proporcionado
            
            datos = request.get_json()
            
            if not datos or not datos.get('usuario') or not datos.get('password'):
                return jsonify({"error": "Usuario y contraseña son requeridos"}), 400
            
            # Simulación de autenticación
            # En un entorno real, verificaríamos contra la base de datos
            usuario = datos.get('usuario')
            password = datos.get('password')
            
            # Simulación de roles para pruebas
            if usuario == 'docente':
                identity = {
                    'id': 42,
                    'usuario': 'docente',
                    'rol': 'docente'
                }
            elif usuario == 'estudiante':
                identity = {
                    'id': 103,
                    'usuario': 'estudiante',
                    'rol': 'estudiante'
                }
            elif usuario == 'admin':
                identity = {
                    'id': 1,
                    'usuario': 'admin',
                    'rol': 'admin'
                }
            else:
                return jsonify({"error": "Credenciales inválidas"}), 401
            
            # Generar token
            access_token = create_access_token(identity=identity)
            
            return jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "access_token": access_token,
                "usuario": identity
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return auth_bp