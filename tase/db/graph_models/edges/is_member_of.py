from typing import Optional

from .base_edge import BaseEdge
from ..vertices import User, Chat


class IsMemberOf(BaseEdge):
    """
    Connection from `User` to `Chat`.
    """

    _collection_edge_name = 'is_member_of'

    _from_vertex_collections = [User]
    _to_vertex_collections = [Chat]

    @staticmethod
    def parse_from_user_and_chat(user: 'User', chat: 'Chat') -> Optional['IsMemberOf']:
        if chat is None or user is None:
            return None

        key = f'{user.key}@{chat.key}'
        return IsMemberOf(
            key=key,
            from_node=user,
            to_node=chat,
        )
