from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Chat


class LinkedChat(BaseEdge):
    """Connection from `Chat` to `Chat`"""

    _collection_name = "linked_chat"
    schema_version = 1

    _from_vertex_collections = (Chat,)
    _to_vertex_collections = (Chat,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Chat,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional["LinkedChat"]:
        key = LinkedChat.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return LinkedChat(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class LinkedChatMethods:
    pass
