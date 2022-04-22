from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import User, Chat


@dataclass
class MemberOf(BaseEdge):
    """
    Connection from `User` to `Chat`.
    """

    _collection_edge_name = 'member_of'

    @staticmethod
    def parse_from_user_and_chat(user: 'User', chat: 'Chat') -> Optional['MemberOf']:
        if chat is None or user is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{user.key}:{chat.key}'
        return MemberOf(
            id=None,
            key=key,
            rev=None,
            from_node=user,
            to_node=chat,
            created_at=ts,
            modified_at=ts,
        )
