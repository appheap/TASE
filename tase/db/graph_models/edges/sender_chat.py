from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import Audio, Chat


@dataclass
class SenderChat(BaseEdge):
    """Connection from `Audio` to `Chat`"""

    _collection_edge_name = 'sender_chat'

    @staticmethod
    def parse_from_audio_and_chat(audio: 'Audio', chat: 'Chat') -> Optional['SenderChat']:
        if audio is None and chat is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f"{audio.key}:{chat.key}"
        return SenderChat(
            id=None,
            key=key,
            from_node=audio,
            to_node=chat,
            created_at=ts,
            modified_at=ts,
        )
