from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat


class LinkedChat(BaseEdge):
    """Connection from `Chat` to `Chat`"""

    _collection_edge_name = "linked_chat"

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [Chat]

    @staticmethod
    def parse_from_chat_and_chat(
        chat: Chat,
        linked_chat: Chat,
    ) -> Optional["LinkedChat"]:
        key = LinkedChat.get_key(chat, linked_chat)
        if not key:
            return None

        return LinkedChat(
            key=key,
            from_node=chat,
            to_node=linked_chat,
        )

    @classmethod
    def get_key(
        cls,
        chat: Chat,
        linked_chat: Chat,
    ):
        if chat is None or linked_chat is None:
            return ""

        return f"{chat.key}@{linked_chat.key}"
