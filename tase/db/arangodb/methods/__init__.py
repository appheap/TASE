from tase.db.arangodb.methods.document import ArangoDocumentMethods
from tase.db.arangodb.methods.graph import ArangoGraphModels


class ArangoMethods(
    ArangoDocumentMethods,
    ArangoGraphModels,
):
    pass
