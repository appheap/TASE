from __future__ import annotations

from typing import Union

from tase.db.arangodb.base import BaseCollectionAttributes
from tase.db.arangodb.enums import HitMetadataType


class BaseHitMetadata(BaseCollectionAttributes):
    type_: HitMetadataType = HitMetadataType.BASE

    def __getattr__(self, item):
        if item in ("playlist_vertex_key", "is_public_playlist"):
            return None

        raise AttributeError


class AudioHitMetadata(BaseHitMetadata):
    type_ = HitMetadataType.AUDIO

    audio_vertex_key: str


class PlaylistAudioHitMetadata(BaseHitMetadata):
    type_ = HitMetadataType.PLAYLIST_AUDIO

    audio_vertex_key: str
    playlist_vertex_key: str
    is_public_playlist: bool


class PlaylistHitMetadata(BaseHitMetadata):
    type_ = HitMetadataType.PLAYLIST

    playlist_vertex_key: str
    is_public_playlist: bool


HitMetadata = Union[
    AudioHitMetadata,
    PlaylistAudioHitMetadata,
    PlaylistHitMetadata,
]
