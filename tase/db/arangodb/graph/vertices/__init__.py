from .base_vertex import BaseVertex
from .dummy_vertex import DummyVertex, DummyVertexMethods
from .user import User

vertex_classes = [
    DummyVertex,
    User,
]


class ArangoVertexMethods(
    DummyVertexMethods,
):
    pass
