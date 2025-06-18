from infra.db.Querys import Query

class CollectionMongo:
    def __init__(self, nombreColeccion:str=None, opciones: dict=None):
        self.query = Query(nombreColeccion)
        self.nombreColeccion = nombreColeccion
        self.opciones = opciones
        self.columnas = []
        self.validador = {}
        self.valuesIndex = None
        self.unique = None

    def initCollection(self):
        if 'validador' in self.opciones.keys():
            self.validador = self.opciones['validadorTabla']
        if 'values_index' in self.opciones.keys():
            self.valuesIndex = self.opciones['values_index']
        if 'unique' in self.opciones.keys():
            self.unique = self.opciones['unique']
        if 'columns' in self.opciones.keys():
            self.columnas = self.opciones['columns']

    def crearColeccion(self):
        self.initCollection()
        if self.nombreColeccion and len(self.nombreColeccion) > 0 and self.validador:
            self.query.crearColeccion({'nombre_coleccion':self.nombreColeccion, 'validador':self.validador})
            self.query.valorUnico(self.unique, self.valuesIndex, self.nombreColeccion)
            return f"Creacion exitosa de la coleccion {self.nombreColeccion}. uwu"
        return f"Que valores estas pasando alv >:v mira: {self.nombreColeccion} y {self.validador}"
        