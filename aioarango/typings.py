__all__ = [
    "Fields",
    "Headers",
    "Json",
    "Jsons",
    "Params",
    "T",
    "Result",
    "ArangoIndex",
]

from typing import Any, Dict, List, MutableMapping, Sequence, Union, TypeVar

from aioarango.models.index import (
    EdgeIndex,
    FullTextIndex,
    GeoIndex,
    HashIndex,
    InvertedIndex,
    PersistentIndex,
    PrimaryIndex,
    SkipListIndex,
    TTLIndex,
    MultiDimensionalIndex,
)

Json = Dict[str, Any]
Jsons = List[Json]
Params = MutableMapping[str, Union[bool, int, str]]
Headers = MutableMapping[str, str]
Fields = Union[str, Sequence[str]]

T = TypeVar("T")

# Result = Union[T, AsyncJob[T], BatchJob[T], None] # fixme
Result = Union[T, None]

ArangoIndex = Union[
    EdgeIndex,
    FullTextIndex,
    GeoIndex,
    HashIndex,
    InvertedIndex,
    PersistentIndex,
    PrimaryIndex,
    SkipListIndex,
    TTLIndex,
    MultiDimensionalIndex,
]
