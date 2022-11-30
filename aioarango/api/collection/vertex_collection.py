from .base_collection import BaseCollection


class VertexCollection(BaseCollection):
    """
    Vertex collection API wrapper.
    """

    def __repr__(self) -> str:
        return f"<VertexCollection {self.name}>"
