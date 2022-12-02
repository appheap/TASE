from __future__ import annotations

__all__ = [
    "BaseHostResolver",
]

from abc import ABC, abstractmethod
from typing import Optional, Set

from pydantic import BaseModel, Field, validator


class BaseHostResolver(BaseModel, ABC):
    """Abstract base class for host resolvers."""

    host_count: int = Field(default=1)
    max_tries: int | None

    @validator("max_tries")
    def validate_max_tries(cls, value, values):
        host_count = values["host_count"]

        if type(host_count) != int:
            raise ValueError("Invalid type for `host_count`")

        max_tries = value or host_count * 3
        if max_tries < host_count:
            raise ValueError("max_tries cannot be less than `host_count`")

        return max_tries

    @abstractmethod
    def get_host_index(
        self,
        indexes_to_filter: Optional[Set[int]] = None,
    ) -> int:
        raise NotImplementedError
