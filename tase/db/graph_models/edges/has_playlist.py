from typing import Optional

from .base_edge import BaseEdge
from ..vertices import User, Playlist


class HasPlaylist(BaseEdge):
    """
    Connection from `User` to `Playlist`.
    """

    _collection_edge_name = 'has_playlist'

    _from_vertex_collections = [User._vertex_name]
    _to_vertex_collections = [Playlist._vertex_name]

    @staticmethod
    def parse_from_user_and_playlist(user: 'User', playlist: 'Playlist') -> Optional['HasPlaylist']:
        if user is None or playlist is None:
            return None

        key = f'{user.key}:{playlist.key}'
        return HasPlaylist(
            key=key,
            from_node=user,
            to_node=playlist,
        )
