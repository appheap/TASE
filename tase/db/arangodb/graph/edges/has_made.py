from typing import Optional, Union

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Query, User


class HasMade(BaseEdge):
    """
    Connection from `User` to `Query
    """

    _collection_name = "has_made"
    schema_version = 1

    _from_vertex_collections = (User,)
    _to_vertex_collections = (Query,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: User,
        to_vertex: Query,
        *args,
        **kwargs,
    ) -> Optional["HasMade"]:
        key = HasMade.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return HasMade(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class HasMadeMethods:
    pass
