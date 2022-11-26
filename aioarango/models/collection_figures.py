from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel


class Indexes(BaseModel):
    count: int
    size: int


class EngineIndex(BaseModel):
    type: str
    id: int
    count: int


class Engine(BaseModel):
    documents: int
    indexes: List[EngineIndex]


class CollectionFigures(BaseModel):
    indexes: Indexes
    documents_size: int
    cache_in_use: bool
    cache_size: int
    cache_usage: int
    engine: Optional[Engine]  # only set if the show_details is set to true when running `figures` endpoint.

    @classmethod
    def parse_from_dict(
        cls,
        d: dict,
    ) -> Optional[CollectionFigures]:
        if d is None or not len(d):
            return None

        engine = None
        if d.get("engine", None):
            engine = Engine.parse_obj(d["engine"])

        return CollectionFigures(
            indexes=Indexes.parse_obj(d["indexes"]),
            documents_size=d["documentsSize"],
            cache_in_use=d["cacheInUse"],
            cache_size=d["cacheSize"],
            cache_usage=d["cacheUsage"],
            engine=engine,
        )
