from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Download, User


class FromBot(BaseEdge):
    """
    Connection from `Download` to `User`
    """

    _collection_name = "from_bot"
    schema_version = 1

    _from_vertex_collections = [Download]
    _to_vertex_collections = [User]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Download,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}@{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Download,
        to_vertex: User,
        **kwargs,
    ) -> Optional["FromBot"]:
        key = FromBot.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return FromBot(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class FromBotMethods:
    pass
