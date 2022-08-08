"""
This package is used to include models that are neither `vertex` nor `edge`, but they are being used in either a
`vertex` or an `edge`.
"""

from .indexer_metadata import IndexerMetadata
from .restriction import Restriction

__all__ = [
    "IndexerMetadata",
    "Restriction",
]
