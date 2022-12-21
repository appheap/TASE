from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, User


class ViaBot(BaseEdge):
    """Connection from `Audio` to a `User`"""

    __collection_name__ = "via_bot"
    schema_version = 1

    __from_vertex_collections__ = (Audio,)
    __to_vertex_collections__ = (User,)

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
