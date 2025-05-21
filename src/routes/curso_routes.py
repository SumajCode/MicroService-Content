from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

curso_bp = Blueprint('curso', __name__)

def init_curso_routes(curso_controller):
    
    @curso_bp.route('/agregarCurso', methods=['POST'])
    @jwt_required()
    def agregar_curso():
        """
        Agrega un nuevo curso
        """
        try:
            # Verificar que el usuario sea docente o admin
            claims = get_jwt_identity()
            if claims.get('rol') not in ['docente', 'admin']:
                return jsonify({"error": "No tienes permisos para agregar cursos"}), 403
            
            return curso_controller.agregar_curso()
        except Exception as e:
            print(f"Error en ruta agregar_curso: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @curso_bp.route('/editarCurso', methods=['PUT', 'PATCH'])
    @jwt_required()
    def editar_curso():
        """
        Edita un curso existente
        """
        try:
            # Verificar que el usuario sea docente o admin
            claims = get_jwt_identity()
            if claims.get('rol') not in ['docente', 'admin']:
                return jsonify({"error": "No tienes permisos para editar cursos"}), 403
            
            return curso_controller.editar_curso()
        except Exception as e:
            print(f"Error en ruta editar_curso: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @curso_bp.route('/mostrarCursosDocente/<int:docente_id>', methods=['GET'])
    @jwt_required()
    def mostrar_cursos_docente(docente_id):
        """
        Muestra todos los cursos de un docente
        """
        try:
            # Verificar permisos
            claims = get_jwt_identity()
            
            # Si es docente, solo puede ver sus propios cursos
            if claims.get('rol') == 'docente' and claims.get('id') != docente_id:
                return jsonify({"error": "Solo puedes ver tus propios cursos"}), 403
            
            return curso_controller.mostrar_cursos_docente(docente_id)
        except Exception as e:
            print(f"Error en ruta mostrar_cursos_docente: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @curso_bp.route('/mostrarTodosLosCursos', methods=['GET'])
    def mostrar_todos_los_cursos():
        """
        Muestra todos los cursos
        """
        try:
            return curso_controller.mostrar_todos_los_cursos()
        except Exception as e:
            print(f"Error en ruta mostrar_todos_los_cursos: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @curso_bp.route('/eliminarCurso', methods=['DELETE'])
    @jwt_required()
    def eliminar_curso():
        """
        Elimina un curso
        """
        try:
            # Verificar que el usuario sea docente o admin
            claims = get_jwt_identity()
            if claims.get('rol') not in ['docente', 'admin']:
                return jsonify({"error": "No tienes permisos para eliminar cursos"}), 403
            
            return curso_controller.eliminar_curso()
        except Exception as e:
            print(f"Error en ruta eliminar_curso: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    return curso_bp