from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, User


class ViaBot(BaseEdge):
    """Connection from `Audio` to a `User`"""

    _collection_name = "via_bot"
    schema_version = 1

    _from_vertex_collections = (Audio,)
    _to_vertex_collections = (User,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional[ViaBot]:
        key = ViaBot.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return ViaBot(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class ViaBotMethods:
    pass
