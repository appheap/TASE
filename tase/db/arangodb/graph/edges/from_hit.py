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
    def parse(
        cls,
        from_vertex: Download,
        to_vertex: Hit,
        *args,
        **kwargs,
    ) -> Optional["FromHit"]:
        key = FromHit.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return FromHit(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class FromHitMethods:
    pass
