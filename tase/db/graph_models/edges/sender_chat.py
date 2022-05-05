from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, Chat


class SenderChat(BaseEdge):
    """Connection from `Audio` to `Chat`"""

    _collection_edge_name = 'sender_chat'

    _from_vertex_collections = [Audio]
    _to_vertex_collections = [Chat]

    @staticmethod
    def parse_from_audio_and_chat(audio: 'Audio', chat: 'Chat') -> Optional['SenderChat']:
        if audio is None and chat is None:
            return None

        key = f"{audio.key}@{chat.key}"
        return SenderChat(
            key=key,
            from_node=audio,
            to_node=chat,
        )
