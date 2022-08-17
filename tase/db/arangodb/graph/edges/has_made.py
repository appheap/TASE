from pydantic.typing import Optional, Union

from .base_edge import BaseEdge
from ..vertices import InlineQuery, Query, User


class HasMade(BaseEdge):
    """
    Connection from `User` to `InlineQuery` or `Query
    """

    _collection_name = "has_made"
    schema_version = 1

    _from_vertex_collections = [User]
    _to_vertex_collections = [InlineQuery, Query]

    @classmethod
    def parse_key(
        cls,
        from_vertex: User,
        to_vertex: Union[InlineQuery, Query],
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: User,
        to_vertex: Union[InlineQuery, Query],
        *args,
        **kwargs,
    ) -> Optional["HasMade"]:
        key = HasMade.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return HasMade(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class HasMadeMethods:
    pass
