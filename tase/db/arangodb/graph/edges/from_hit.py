from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Interaction, Hit


class FromHit(BaseEdge):
    """
    Connection from `Download` to `Hit`
    """

    _collection_name = "from_hit"
    schema_version = 1

    _from_vertex_collections = (Interaction,)
    _to_vertex_collections = (Hit,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Interaction,
        to_vertex: Hit,
        *args,
        **kwargs,
    ) -> Optional[FromHit]:
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
