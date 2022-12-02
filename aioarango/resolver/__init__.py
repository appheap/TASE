__all__ = [
    "BaseHostResolver",
    "RandomHostResolver",
    "RoundRobinHostResolver",
    "SingleHostResolver",
    "HostResolver",
]

from typing import Union

HostResolver = Union[
    "RandomBaseHostResolver",
    "RoundRobinBaseHostResolver",
    "SingleBaseHostResolver",
]

from .base_resolver import BaseHostResolver
from .random_host_resolver import RandomHostResolver
from .round_robin_resolver import RoundRobinHostResolver
from .single_host_resolver import SingleHostResolver
