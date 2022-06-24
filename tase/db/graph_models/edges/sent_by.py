from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, Chat


class SentBy(BaseEdge):
    """Connection from `Audio` to `Chat`"""

    _collection_edge_name = "sent_by"

    _from_vertex_collections = [Audio]
    _to_vertex_collections = [Chat]

    @staticmethod
    def parse_from_audio_and_chat(
        audio: "Audio",
        chat: "Chat",
    ) -> Optional["SentBy"]:
        if audio is None and chat is None:
            return None

        key = f"{audio.key}@{chat.key}"
        return SentBy(
            key=key,
            from_node=audio,
            to_node=chat,
        )
