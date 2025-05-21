import cloudinary
import cloudinary.uploader
from flask import jsonify, request
from datetime import datetime

class CursoController:
    def __init__(self, curso_model):
        self.curso_model = curso_model
    
    def agregar_curso(self):
        """
        Endpoint para agregar un nuevo curso
        """
        try:
            # Obtener datos del formulario o JSON
            if request.is_json:
                datos = request.get_json()
            else:
                datos = request.form.to_dict()
            
            # Validar datos requeridos
            if not datos.get('nombre'):
                return jsonify({"error": "El nombre del curso es requerido"}), 400
                
            if not datos.get('docente_id'):
                return jsonify({"error": "El ID del docente es requerido"}), 400
            
            # Convertir docente_id a entero
            try:
                datos['docente_id'] = int(datos['docente_id'])
            except ValueError:
                return jsonify({"error": "El ID del docente debe ser un número"}), 400
            
            # Procesar temas (si vienen como string, convertir a lista)
            if 'temas' in datos:
                if isinstance(datos['temas'], str):
                    datos['temas'] = [tema.strip() for tema in datos['temas'].split(',')]
            else:
                datos['temas'] = []
            
            # Procesar archivos adjuntos
            archivos = []
            if request.files and 'archivos' in request.files:
                archivos_subidos = request.files.getlist('archivos')
                
                for archivo in archivos_subidos:
                    # Subir archivo a Cloudinary
                    resultado = cloudinary.uploader.upload(
                        archivo,
                        folder=f"cursos/materiales",
                        resource_type="auto"
                    )
                    
                    archivos.append({
                        "url": resultado["secure_url"],
                        "nombre": archivo.filename,
                        "tipo": archivo.content_type,
                        "subido_en": datetime.utcnow().isoformat()
                    })
            
            # Agregar archivos a los datos
            datos['archivos'] = archivos
            
            # Crear el curso
            curso_id = self.curso_model.agregar_curso(datos)
            
            return jsonify({
                "mensaje": "Curso agregado exitosamente",
                "curso_id": curso_id
            }), 201
            
        except Exception as e:
            print(f"Error al agregar curso: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def editar_curso(self):
        """
        Endpoint para editar un curso existente
        """
        try:
            # Obtener ID del curso
            curso_id = request.args.get('id')
            if not curso_id:
                return jsonify({"error": "El ID del curso es requerido"}), 400
            
            # Verificar si el curso existe
            curso = self.curso_model.obtener_curso_por_id(curso_id)
            if not curso:
                return jsonify({"error": "Curso no encontrado"}), 404
            
            # Obtener datos del formulario o JSON
            if request.is_json:
                datos = request.get_json()
            else:
                datos = request.form.to_dict()
            
            # Procesar temas (si vienen como string, convertir a lista)
            if 'temas' in datos and isinstance(datos['temas'], str):
                datos['temas'] = [tema.strip() for tema in datos['temas'].split(',')]
            
            # Procesar archivos adjuntos (si hay nuevos)
            if request.files and 'archivos' in request.files:
                archivos_subidos = request.files.getlist('archivos')
                
                # Si no hay archivos en el curso, inicializar la lista
                if 'archivos' not in datos:
                    datos['archivos'] = curso.get('archivos', [])
                
                for archivo in archivos_subidos:
                    # Subir archivo a Cloudinary
                    resultado = cloudinary.uploader.upload(
                        archivo,
                        folder=f"cursos/materiales",
                        resource_type="auto"
                    )
                    
                    datos['archivos'].append({
                        "url": resultado["secure_url"],
                        "nombre": archivo.filename,
                        "tipo": archivo.content_type,
                        "subido_en": datetime.utcnow().isoformat()
                    })
            
            # Editar el curso
            resultado = self.curso_model.editar_curso(curso_id, datos)
            
            if resultado:
                return jsonify({"mensaje": "Curso editado exitosamente"}), 200
            else:
                return jsonify({"error": "No se pudo editar el curso"}), 500
            
        except Exception as e:
            print(f"Error al editar curso: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def mostrar_cursos_docente(self, docente_id):
        """
        Endpoint para mostrar todos los cursos de un docente
        """
        try:
            cursos = self.curso_model.obtener_cursos_por_docente(docente_id)
            return jsonify(cursos), 200
            
        except Exception as e:
            print(f"Error al mostrar cursos por docente: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def mostrar_todos_los_cursos(self):
        """
        Endpoint para mostrar todos los cursos
        """
        try:
            estado = request.args.get('estado')
            cursos = self.curso_model.obtener_todos_los_cursos(estado)
            return jsonify(cursos), 200
            
        except Exception as e:
            print(f"Error al mostrar todos los cursos: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def eliminar_curso(self):
        """
        Endpoint para eliminar un curso
        """
        try:
            # Obtener ID del curso
            curso_id = request.args.get('id')
            if not curso_id:
                return jsonify({"error": "El ID del curso es requerido"}), 400
            
            # Verificar si el curso existe
            curso = self.curso_model.obtener_curso_por_id(curso_id)
            if not curso:
                return jsonify({"error": "Curso no encontrado"}), 404
            
            # Determinar si es eliminación lógica o física
            eliminacion_logica = request.args.get('logica', 'true').lower() == 'true'
            
            # Eliminar el curso
            resultado = self.curso_model.eliminar_curso(curso_id, eliminacion_logica)
            
            if resultado:
                mensaje = "Curso suspendido exitosamente" if eliminacion_logica else "Curso eliminado exitosamente"
                return jsonify({"mensaje": mensaje}), 200
            else:
                return jsonify({"error": "No se pudo eliminar el curso"}), 500
            
        except Exception as e:
            print(f"Error al eliminar curso: {str(e)}")
            return jsonify({"error": str(e)}), 500