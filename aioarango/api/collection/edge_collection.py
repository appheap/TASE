from .base_collection import BaseCollection


class EdgeCollection(BaseCollection):
    """
    ArangoDB edge collection API wrapper.
    """

    def __repr__(self) -> str:
        return f"<EdgeCollection {self.name}>"
