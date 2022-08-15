from tase.db.arangodb.methods.graph.edges import ArangoEdgeMethods

from tase.db.arangodb.methods.graph.vertices import ArangoVertexMethods


class ArangoGraphModels(
    ArangoVertexMethods,
    ArangoEdgeMethods,
):
    pass
