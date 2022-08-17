from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Download, Hit


class FromHit(BaseEdge):
    """
    Connection from `Download` to `Hit`
    """

    _collection_name = "from_hit"
    schema_version = 1

    _from_vertex_collections = [Download]
    _to_vertex_collections = [Hit]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Download,
        to_vertex: Hit,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Download,
        to_vertex: Hit,
        *args,
        **kwargs,
    ) -> Optional["FromHit"]:
        key = FromHit.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return FromHit(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class FromHitMethods:
    pass
