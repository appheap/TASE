from typing import Optional, Set

from aioarango.resolver import BaseHostResolver


class SingleHostResolver(BaseHostResolver):
    """Single host resolver."""

    def get_host_index(
        self,
        indexes_to_filter: Optional[Set[int]] = None,
    ) -> int:
        return 0
