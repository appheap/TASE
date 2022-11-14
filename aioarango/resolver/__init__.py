__all__ = [
    "BaseHostResolver",
    "RandomBaseHostResolver",
    "RoundRobinBaseHostResolver",
    "SingleBaseHostResolver",
    "HostResolver",
]

from typing import Union

HostResolver = Union[
    "RandomBaseHostResolver",
    "RoundRobinBaseHostResolver",
    "SingleBaseHostResolver",
]

from .base_resolver import BaseHostResolver
from .random_host_resolver import RandomBaseHostResolver
from .round_robin_resolver import RoundRobinBaseHostResolver
from .single_host_resolver import SingleBaseHostResolver
