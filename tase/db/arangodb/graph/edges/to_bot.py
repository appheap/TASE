from pydantic.typing import Optional, Union

from .base_edge import BaseEdge
from ..vertices import InlineQuery, Query, User


class ToBot(BaseEdge):
    """
    Connection from `InlineQuery` to `User`
    """

    _collection_name = "to_bot"
    schema_version = 1

    _from_vertex_collections = [InlineQuery, Query]
    _to_vertex_collections = [User]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[InlineQuery, Query],
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Union[InlineQuery, Query],
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional["ToBot"]:
        key = ToBot.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return ToBot(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class ToBotMethods:
    pass
