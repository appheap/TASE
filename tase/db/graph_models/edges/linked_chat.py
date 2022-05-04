from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat


class LinkedChat(BaseEdge):
    """Connection from `Chat` to `Chat`"""

    _collection_edge_name = 'linked_chat'

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [Chat]

    @staticmethod
    def parse_from_chat_and_chat(chat: 'Chat', linked_chat: 'Chat') -> Optional['LinkedChat']:
        if chat is None and linked_chat is None:
            return None

        key = f'{chat.key}:{linked_chat.key}'
        return LinkedChat(
            key=key,
            from_node=chat,
            to_node=linked_chat,
        )
