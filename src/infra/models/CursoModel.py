from db.Collection import CollectionMongo

class Curso(CollectionMongo):
    nombreTabla = 'curso'
    opciones = {
        'validadorTabla':{
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['nombre_curso', 'id_docente', 'id_materia'],
                    'properties': {
                        'nombre': {'bsonType': 'string'},
                        'id_docente': {'bsonType': 'int'},
                        'id_materia': {'bsonType': 'int'}
                    }
                }
            }
        },
        'values_index':[('id_docente', 1), ('id_materia', 1)],
        'unique':'id_docente'
    }
    
    def __init__(self):
        super().__init__(self.nombreTabla, self.validadorTabla)