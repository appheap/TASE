from .audio import Audio, AudioMethods
from .base_document import BaseDocument
from .playlist import Playlist, PlaylistMethods

elasticsearch_indices = [
    Audio,
    Playlist,
]


class ElasticSearchMethods(
    AudioMethods,
    PlaylistMethods,
):
    pass


__all__ = [
    "BaseDocument",
    "Audio",
    "Playlist",
    "elasticsearch_indices",
    "ElasticSearchMethods",
]
