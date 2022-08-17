from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat


class LinkedChat(BaseEdge):
    """Connection from `Chat` to `Chat`"""

    _collection_name = "linked_chat"
    schema_version = 1

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [Chat]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Chat,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Chat,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional["LinkedChat"]:
        key = LinkedChat.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return LinkedChat(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class LinkedChatMethods:
    pass
