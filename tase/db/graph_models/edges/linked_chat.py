from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import Audio, Chat


@dataclass
class LinkedChat(BaseEdge):
    """Connection from `Chat` to `Chat`"""

    _collection_edge_name = 'linked_chat'

    @staticmethod
    def parse_from_chat_and_chat(chat: 'Chat', linked_chat: 'Chat') -> Optional['LinkedChat']:
        if chat is None and linked_chat is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{chat.key}:{linked_chat.key}'
        return LinkedChat(
            id=None,
            key=key,
            from_node=chat,
            to_node=linked_chat,
            created_at=ts,
            modified_at=ts,
        )
