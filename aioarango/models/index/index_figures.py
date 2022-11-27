from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class IndexFigures(BaseModel):
    memory: int
    cache_in_use: bool
    cache_size: int
    cache_usage: int

    @classmethod
    def parse_from_dict(
        cls,
        d: dict,
    ) -> Optional[IndexFigures]:
        if d is None or not len(d):
            return None

        return IndexFigures(
            memory=d["memory"],
            cache_in_use=d["cacheInUse"],
            cache_size=d["cacheSize"],
            cache_usage=d["cacheUsage"],
        )
