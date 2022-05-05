from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, Playlist, Hit


class HasAudio(BaseEdge):
    """
    Connection from `Playlist` or `Hit` to `Audio`.
    """

    _collection_edge_name = 'has_audio'

    _from_vertex_collections = [Playlist, Hit]
    _to_vertex_collections = [Audio]

    @staticmethod
    def parse_from_playlist_and_audio(playlist: 'Playlist', audio: 'Audio') -> Optional['HasAudio']:
        if playlist is None or audio is None:
            return None

        key = f'{playlist.key}@{audio.key}'
        return HasAudio(
            key=key,
            from_node=playlist,
            to_node=audio,
        )

    @staticmethod
    def parse_from_hit_and_audio(hit: 'Hit', audio: 'Audio') -> Optional['HasAudio']:
        if hit is None or audio is None:
            return None

        key = f"{hit.key}@{audio.key}"
        return HasAudio(
            key=key,
            from_node=hit,
            to_node=audio,
        )
