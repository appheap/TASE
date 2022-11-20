from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from aioarango.enums import CollectionStatus, CollectionType


class ArangoCollection(BaseModel):
    id: str
    name: str
    status: CollectionStatus
    type: CollectionType
    is_system: bool
    globally_unique_id: str

    @classmethod
    def parse_from_dict(cls, obj: dict) -> Optional[ArangoCollection]:
        if obj is None or not len(obj):
            return None

        return ArangoCollection(
            id=obj["id"],
            name=obj["name"],
            status=obj["status"],
            type=obj["type"],
            is_system=obj["isSystem"],
            globally_unique_id=obj["globallyUniqueId"],
        )
