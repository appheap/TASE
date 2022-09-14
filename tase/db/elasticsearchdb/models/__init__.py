from .audio import Audio
from .base_document import BaseDocument

elasticsearch_indices = [
    Audio,
]
__all__ = [
    "BaseDocument",
    "Audio",
    "elasticsearch_indices",
]
