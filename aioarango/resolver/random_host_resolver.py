import random
from typing import Optional, Set

from aioarango.resolver import BaseHostResolver


class RandomBaseHostResolver(BaseHostResolver):
    """Random host resolver."""

    def get_host_index(
        self,
        indexes_to_filter: Optional[Set[int]] = None,
    ) -> int:
        host_index = None
        indexes_to_filter = indexes_to_filter or set()
        while host_index is None or host_index in indexes_to_filter:
            host_index = random.randint(0, self.host_count - 1)

        return host_index
