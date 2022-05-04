from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, Playlist


class HasAudio(BaseEdge):
    """
    Connection from `Playlist` to `Audio`.
    """

    _collection_edge_name = 'has_audio'

    _from_vertex_collections = [Playlist]
    _to_vertex_collections = [Audio]

    @staticmethod
    def parse_from_playlist_and_audio(playlist: 'Playlist', audio: 'Audio') -> Optional['HasAudio']:
        if playlist is None or audio is None:
            return None

        key = f'{playlist.key}:{audio.key}'
        return HasAudio(
            key=key,
            from_node=playlist,
            to_node=audio,
        )
