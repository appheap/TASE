from .base_collection import BaseCollection


class StandardCollection(BaseCollection):
    """Standard ArangoDB collection API wrapper."""

    def __repr__(self) -> str:
        return f"<StandardCollection {self.name}>"
