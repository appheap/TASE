from typing import Optional

from .base_edge import BaseEdge
from .has import Has
from ..vertices import (
    Audio,
    Playlist,
    User,
)


class Had(BaseEdge):
    """ """

    _collection_edge_name = "had"

    deleted_at: int
    metadata_created_at: int
    metadata_modified_at: int

    _from_vertex_collections = [
        User,
        Playlist,
    ]
    _to_vertex_collections = [
        Playlist,
        Audio,
    ]

    @staticmethod
    def parse_from_user_and_playlist(
        user: "User",
        playlist: "Playlist",
        deleted_at: int,
        has: Has,
    ) -> Optional["Had"]:
        if user is None or playlist is None or deleted_at is None or has is None:
            return None

        key = f"{user.key}@{playlist.key}:{deleted_at}"
        return Had(
            key=key,
            from_node=user,
            to_node=playlist,
            deleted_at=deleted_at,
            metadata_created_at=has.created_at,
            metadata_modified_at=has.modified_at,
        )

    @staticmethod
    def parse_from_playlist_and_audio(
        playlist: "Playlist",
        audio: "Audio",
        deleted_at: int,
        has: Has,
    ) -> Optional["Had"]:
        if playlist is None or audio is None or deleted_at is None or has is None:
            return None

        key = f"{playlist.key}@{audio.key}:{deleted_at}"
        return Had(
            key=key,
            from_node=playlist,
            to_node=audio,
            deleted_at=deleted_at,
            metadata_created_at=has.created_at,
            metadata_modified_at=has.modified_at,
        )
