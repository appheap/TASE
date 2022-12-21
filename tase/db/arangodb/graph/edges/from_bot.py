from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Interaction, User


class FromBot(BaseEdge):
    """
    Connection from `Interaction` to `User`
    """

    __collection_name__ = "from_bot"
    schema_version = 1

    __from_vertex_collections__ = (Interaction,)
    __to_vertex_collections__ = (User,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Interaction,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional[FromBot]:
        key = FromBot.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return FromBot(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class FromBotMethods:
    pass
