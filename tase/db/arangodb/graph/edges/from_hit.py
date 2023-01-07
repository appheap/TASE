from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import AudioInteraction, Hit, PlaylistInteraction


class FromHit(BaseEdge):
    """
    Connection from `Download` to `Hit`
    """

    __collection_name__ = "from_hit"
    schema_version = 1

    __from_vertex_collections__ = (
        AudioInteraction,
        PlaylistInteraction,
    )
    __to_vertex_collections__ = (Hit,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: AudioInteraction,
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
