from typing import Optional

from .base_edge import BaseEdge
from ..vertices import User, Chat


class Creator(BaseEdge):
    """
    Connection from `Chat` to `User`.
    """

    _collection_edge_name = 'creator'

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [User]

    @staticmethod
    def parse_from_chat_and_user(chat: 'Chat', creator: 'User') -> Optional['Creator']:
        if chat is None or creator is None:
            return None

        key = f'{chat.key}@{creator.key}'
        return Creator(
            key=key,
            from_node=chat,
            to_node=creator,
        )
