from infra.db.Collection import CollectionMongo

class Modulo(CollectionMongo):
    nombreColeccion = 'modulo'
    opciones = {
        'validadorTabla':{
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['id_modulo', 'id_docente', 'id_materia', 'title'],
                    'properties': {
                        'id_modulo': {'bsonType': 'objectId'},
                        'id_docente': {'bsonType': 'int'},
                        'id_materia': {'bsonType': 'int'},
                        'title': {'bsonType': 'string'},
                        'desciption': {'bsonType': 'string'},
                        'image': {
                            'bsonType': 'string',
                            'pattern': '^.*\\.(jpg|png|jpeg)$'},
                        'timestamp': {'bsonType': 'timestamp'}
                    }
                }
            }
        },
        'values_index':[('id_modulo', 1), ('id_docente', 1), ('id_materia', 1)],
        'unique':'id_modulo',
        'columns':['id_modulo', 'id_docente', 'id_materia', 'title', 'desciption', 'image', 'timestamp']
    }

    def __init__(self):
        super().__init__(self.nombreColeccion, self.opciones)