from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from tase.db.arangodb.enums import InteractionType


class InteractionCount(BaseModel):
    vertex_key: str
    interaction_type: InteractionType
    count: int
    is_active: bool

    @classmethod
    def parse(
        cls,
        db_object: dict,
    ) -> Optional[InteractionCount]:
        if db_object is None or not len(db_object):
            return None

        vertex_key = db_object.get("vertex_key", None)
        interaction_type = db_object.get("interaction_type", None)
        count = db_object.get("count_", None)
        is_active = db_object.get("is_active", None)

        if vertex_key is not None and interaction_type is not None and count is not None and is_active is not None:
            return InteractionCount(
                vertex_key=vertex_key,
                interaction_type=interaction_type,
                count=count,
                is_active=is_active,
            )

        return None
