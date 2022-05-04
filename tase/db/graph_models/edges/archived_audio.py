from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio


class ArchivedAudio(BaseEdge):
    """
    Connection from `Audio` to the archived `Audio`
    """

    _collection_edge_name = 'archived_audio'

    _from_vertex_collections = [Audio]
    _to_vertex_collections = [Audio]

    @staticmethod
    def parse_from_audio_and_audio(audio: 'Audio', archived_audio: 'Audio') -> Optional['ArchivedAudio']:
        if audio is None or archived_audio is None:
            return None

        key = f'{audio.key}:{archived_audio.key}'
        return ArchivedAudio(
            key=key,
            from_node=audio,
            to_node=archived_audio,
        )
