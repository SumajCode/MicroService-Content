from infra.db.Collection import CollectionMongo

class Contenido(CollectionMongo):
    nombreColeccion = 'contenido'
    opciones = {
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
                        'items': {
                            'bsonType': 'string',
                            'pattern':'^.*\\.(pdf|jpg|png|docx|py|txt|html|mp4)$'}},
                    'type': {'bsonType': 'string'},
                    'time_deliver': {'bsonType': 'date'},
                    'content': {
                        'bsonType': 'object',
                        'properties': {
                            'description': {'bsonType': 'string'},
                            'rules':{
                                'bsonType': 'object',
                                'properties': {
                                    'classes': {
                                        'bsonType': 'object',
                                        'properties': {
                                            'classNames': {
                                                'bsonType': 'array',
                                                'items': {'bsonType': 'string'}
                                            },
                                            'classCodes': {
                                                'bsonType': 'array',
                                                'items': {'bsonType': 'string'}
                                            },
                                        }
                                    },
                                    'functions': {
                                        'bsonType': 'object',
                                        'properties': {
                                            'functionNames': {
                                                'bsonType': 'array',
                                                'items': {'bsonType': 'string'}
                                            },
                                            'functionCodes': {
                                                'bsonType': 'array',
                                                'items': {'bsonType': 'string'}
                                            },
                                        }
                                    },
                                    'imports': {
                                        'bsonType': 'array',
                                        'items': {'bsonType': 'string'}
                                    }
                                }
                            }
                        }
                    },
                    'status': {'bsonType': 'string'},
                    'points': {'bsonType': 'double'},
                    'timestamp': {'bsonType': 'date'},
                }
            }
        },
        'values_index':[('id_contenido', 1), ('id_modulo', 1)],
        'unique':'id_contenido',
        'columns':['id_contenido', 'id_modulo', 'title', 'type', 'files', 'time_deliver', 'content', 'status', 'points', 'timestamp']
    }

    def __init__(self):
        super().__init__(self.nombreColeccion, self.opciones)