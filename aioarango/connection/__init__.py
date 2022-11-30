__all__ = [
    "BaseConnection",
    "BasicConnection",
    "Connection",
]

from typing import Union

Connection = Union[
    "BasicConnection",
]

from .base_connection import BaseConnection
from .basic_connection import BasicConnection
