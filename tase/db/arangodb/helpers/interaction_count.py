from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from tase.db.arangodb.enums import InteractionType


class InteractionCount(BaseModel):
    audio_key: str
    interaction_type: InteractionType
    count: int

    @classmethod
    def parse(
        cls,
        db_object: dict,
    ) -> Optional[InteractionCount]:
        if db_object is None or not len(db_object):
            return None

        audio_key = db_object.get("audio_key", None)
        interaction_type = db_object.get("interaction_type", None)
        count = db_object.get("count_", None)

        if audio_key is not None and interaction_type is not None and count is not None:
            return InteractionCount(
                audio_key=audio_key,
                interaction_type=interaction_type,
                count=count,
            )

        return None
