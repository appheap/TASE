from typing import Optional, Set

from pydantic import Field

from aioarango.resolver import BaseHostResolver


class RoundRobinHostResolver(BaseHostResolver):
    """Round-robin host resolver."""

    _index: int = Field(default=-1)

    class Config:
        underscore_attrs_are_private = True

    def get_host_index(
        self,
        indexes_to_filter: Optional[Set[int]] = None,
    ) -> int:
        self._index = (self._index + 1) % self.host_count
        return self._index
