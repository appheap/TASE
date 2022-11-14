__all__ = [
    "Fields",
    "Headers",
    "Json",
    "Jsons",
    "Params",
    "T",
]

from typing import Any, Dict, List, MutableMapping, Sequence, Union, TypeVar

Json = Dict[str, Any]
Jsons = List[Json]
Params = MutableMapping[str, Union[bool, int, str]]
Headers = MutableMapping[str, str]
Fields = Union[str, Sequence[str]]

T = TypeVar("T")
