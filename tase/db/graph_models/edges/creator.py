from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import User, Chat


@dataclass
class Creator(BaseEdge):
    """
    Connection from `Chat` to `User`.
    """

    @staticmethod
    def parse_from_chat_and_user(chat: 'Chat', creator: 'User') -> Optional['Creator']:
        if chat is None or creator is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        return Creator(
            id=None,
            key=None,
            from_node=chat,
            to_node=creator,
            created_at=ts,
            modified_at=ts,
        )
