from tase.db.arangodb.graph.edges import ArangoEdgeMethods
from tase.db.arangodb.graph.vertices import ArangoVertexMethods


class ArangoGraphModels(
    ArangoVertexMethods,
    ArangoEdgeMethods,
):
    pass
