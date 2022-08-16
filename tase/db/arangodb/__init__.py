from .arangodb import ArangoDB
from .document import ArangoDocumentMethods
from .graph import ArangoGraphModels


class ArangoMethods(
    ArangoDocumentMethods,
    ArangoGraphModels,
):
    pass
