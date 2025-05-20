from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

cursos_bp = Blueprint('cursos', __name__)

def init_cursos_routes(curso_model):
    
    @cursos_bp.route('/curso', methods=['POST'])
    @jwt_required()
    def crear_curso():
        """
        Crea un nuevo curso
        """
        try:
            # Obtener datos del request
            datos = request.get_json()
            
            # Validar datos requeridos
            if not datos.get('nombre'):
                return jsonify({"error": "El nombre del curso es requerido"}), 400
                
            if not datos.get('docente_id'):
                return jsonify({"error": "El ID del docente es requerido"}), 400
            
            # Verificar que el usuario sea docente o admin
            claims = get_jwt_identity()
            if claims.get('rol') not in ['docente', 'admin']:
                return jsonify({"error": "No tienes permisos para crear cursos"}), 403
            
            # Crear curso
            curso_id = curso_model.crear(datos)
            
            return jsonify({
                "mensaje": "Curso creado exitosamente",
                "curso_id": curso_id
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @cursos_bp.route('/cursos/docente/<int:docente_id>', methods=['GET'])
    @jwt_required()
    def obtener_cursos_por_docente(docente_id):
        """
        Obtiene todos los cursos de un docente
        """
        try:
            # Verificar permisos
            claims = get_jwt_identity()
            if claims.get('rol') not in ['docente', 'admin']:
                return jsonify({"error": "No tienes permisos para ver estos cursos"}), 403
                
            # Si es docente, solo puede ver sus propios cursos
            if claims.get('rol') == 'docente' and claims.get('id') != docente_id:
                return jsonify({"error": "Solo puedes ver tus propios cursos"}), 403
            
            # Obtener cursos
            cursos = curso_model.obtener_por_docente(docente_id)
            
            return jsonify(cursos), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @cursos_bp.route('/cursos/todos', methods=['GET'])
    def obtener_cursos_por_estado():
        """
        Obtiene todos los cursos con un estado específico
        """
        try:
            estado = request.args.get('estado', 'publico')
            cursos = curso_model.obtener_por_estado(estado)
            
            return jsonify(cursos), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return cursos_bp