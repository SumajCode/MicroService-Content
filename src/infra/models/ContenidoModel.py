from db.Collection import CollectionMongo

class Contenido(CollectionMongo):
    nombreColeccion = 'contenido'
    opciones = {
        'validadorTabla':{
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['id_contenido', 'id_modulo', 'title', 'type'],
                    'properties': {
                        'id_contenido': {'bsonType': 'objectId'},
                        'id_modulo': {'bsonType': 'string'},
                        'title': {'bsonType': 'string'},
                        'files': {
                            'bsonType': 'array',
                            'items': {'bsonType': 'string'}},
                        'type': {'bsonType': 'string'},
                        'time_deliver': {'bsonType': 'date'},
                        'content': {
                            'bsonType': 'object',
                            'description': {'bsonType': 'string'},
                            'rules':{
                                'bsonType': 'object',
                                'classes': {
                                    'bsonType': 'object',
                                    'classNames': {
                                        'bsonType': 'array',
                                        'items': {'bsonType': 'string'}
                                    },
                                    'classCodes': {
                                        'bsonType': 'array',
                                        'items': {'bsonType': 'string'}
                                    },
                                },
                                'functions': {
                                    'bsonType': 'object',
                                    'functionNames': {
                                        'bsonType': 'array',
                                        'items': {'bsonType': 'string'}
                                    },
                                    'functionCodes': {
                                        'bsonType': 'array',
                                        'items': {'bsonType': 'string'}
                                    },
                                },
                                'imports': {
                                    'bsonType': 'array',
                                    'items': {'bsonType': 'string'}
                                }
                            }
                        },
                        'timestamp': {'bsonType': 'timestamp'},
                        'points': {'bsonType': 'double'},
                    }
                }
            }
        },
        'values_index':[('id_contenido', 1), ('id_modulo', 1)],
        'unique':'id_contenido',
        'columns':['id_contenido', 'id_modulo', 'title', 'files', 'type', 'content']
    }

    def __init__(self):
        super().__init__(self.nombreColeccion, self.opciones)