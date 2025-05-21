from datetime import datetime
from bson import ObjectId

class CursoModel:
    def __init__(self, db):
        self.collection = db.cursos
    
    def agregar_curso(self, datos):
        """
        Agrega un nuevo curso a la base de datos
        """
        nuevo_curso = {
            "nombre": datos.get("nombre"),
            "descripcion": datos.get("descripcion", ""),
            "docente_id": datos.get("docente_id"),
            "estado": datos.get("estado", "borrador"),
            "temas": datos.get("temas", []),
            "archivos": datos.get("archivos", []),
            "creado_en": datetime.utcnow(),
            "actualizado_en": datetime.utcnow()
        }
        
        resultado = self.collection.insert_one(nuevo_curso)
        return str(resultado.inserted_id)
    
    def editar_curso(self, curso_id, datos):
        """
        Edita un curso existente
        """
        # Asegurarse de que no se modifique el ID
        if "_id" in datos:
            del datos["_id"]
        
        # Actualizar la fecha de modificación
        datos["actualizado_en"] = datetime.utcnow()
        
        resultado = self.collection.update_one(
            {"_id": ObjectId(curso_id)},
            {"$set": datos}
        )
        
        return resultado.modified_count > 0
    
    def obtener_cursos_por_docente(self, docente_id):
        """
        Obtiene todos los cursos de un docente específico
        """
        try:
            cursos = list(self.collection.find({"docente_id": int(docente_id)}))
            return self._formatear_cursos(cursos)
        except Exception as e:
            print(f"Error al obtener cursos por docente: {str(e)}")
            return []
    
    def obtener_todos_los_cursos(self, estado=None):
        """
        Obtiene todos los cursos, opcionalmente filtrados por estado
        """
        try:
            filtro = {}
            if estado:
                filtro["estado"] = estado
                
            cursos = list(self.collection.find(filtro))
            return self._formatear_cursos(cursos)
        except Exception as e:
            print(f"Error al obtener todos los cursos: {str(e)}")
            return []
    
    def eliminar_curso(self, curso_id, eliminacion_logica=True):
        """
        Elimina un curso o lo marca como suspendido
        """
        try:
            if eliminacion_logica:
                # Eliminación lógica (cambiar estado a "suspendido")
                resultado = self.collection.update_one(
                    {"_id": ObjectId(curso_id)},
                    {
                        "$set": {
                            "estado": "suspendido",
                            "fecha_suspension": datetime.utcnow(),
                            "actualizado_en": datetime.utcnow()
                        }
                    }
                )
                return resultado.modified_count > 0
            else:
                # Eliminación física
                resultado = self.collection.delete_one({"_id": ObjectId(curso_id)})
                return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar curso: {str(e)}")
            return False
    
    def obtener_curso_por_id(self, curso_id):
        """
        Obtiene un curso por su ID
        """
        try:
            curso = self.collection.find_one({"_id": ObjectId(curso_id)})
            if curso:
                curso["_id"] = str(curso["_id"])
                return curso
            return None
        except Exception as e:
            print(f"Error al obtener curso por ID: {str(e)}")
            return None
    
    def _formatear_cursos(self, cursos):
        """
        Formatea los IDs de ObjectId a string para la respuesta JSON
        """
        for curso in cursos:
            curso["_id"] = str(curso["_id"])
        return cursos