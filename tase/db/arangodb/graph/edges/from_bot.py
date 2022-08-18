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
    def parse(
        cls,
        from_vertex: Download,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional["FromBot"]:
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
