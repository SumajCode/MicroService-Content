from datetime import datetime
from bson import ObjectId

class Curso:
    def __init__(self, db):
        self.collection = db.cursos
    
    def crear(self, datos):
        """
        Crea un nuevo curso en la base de datos
        """
        nuevo_curso = {
            "nombre": datos.get("nombre"),
            "descripcion": datos.get("descripcion", ""),
            "docente_id": datos.get("docente_id"),
            "estado": datos.get("estado", "borrador"),
            "temas": datos.get("temas", []),
            "archivos": [],
            "creado_en": datetime.utcnow(),
            "actualizado_en": datetime.utcnow()
        }
        
        resultado = self.collection.insert_one(nuevo_curso)
        return str(resultado.inserted_id)
    
    def obtener_por_docente(self, docente_id):
        """
        Obtiene todos los cursos de un docente específico
        """
        cursos = list(self.collection.find({"docente_id": int(docente_id)}))
        return self._formatear_cursos(cursos)
    
    def obtener_por_estado(self, estado):
        """
        Obtiene todos los cursos con un estado específico
        """
        cursos = list(self.collection.find({"estado": estado}))
        return self._formatear_cursos(cursos)
    
    def obtener_por_id(self, curso_id):
        """
        Obtiene un curso por su ID
        """
        try:
            curso = self.collection.find_one({"_id": ObjectId(curso_id)})
            if curso:
                curso["_id"] = str(curso["_id"])
                return curso
            return None
        except:
            return None
    
    def _formatear_cursos(self, cursos):
        """
        Formatea los IDs de ObjectId a string para la respuesta JSON
        """
        for curso in cursos:
            curso["_id"] = str(curso["_id"])
        return cursos