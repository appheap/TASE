from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Query, User


class ToBot(BaseEdge):
    """
    Connection from `Query` to `User`
    """

    __collection_name__ = "to_bot"
    schema_version = 1

    __from_vertex_collections__ = (Query,)
    __to_vertex_collections__ = (User,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Query,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional[ToBot]:
        key = ToBot.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return ToBot(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class ToBotMethods:
    pass
