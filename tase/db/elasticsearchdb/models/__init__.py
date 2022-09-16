from .audio import Audio, AudioMethods
from .base_document import BaseDocument

elasticsearch_indices = [
    Audio,
]


class ElasticSearchMethods(
    AudioMethods,
):
    pass


__all__ = [
    "BaseDocument",
    "Audio",
    "elasticsearch_indices",
    "ElasticSearchMethods",
]
