from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from tase.db.arangodb.enums import AudioInteractionType


class AudioInteractionCount(BaseModel):
    audio_key: str
    interaction_type: AudioInteractionType
    count: int
    is_active: bool

    @classmethod
    def parse(
        cls,
        db_object: dict,
    ) -> Optional[AudioInteractionCount]:
        if db_object is None or not len(db_object):
            return None

        audio_key = db_object.get("audio_key", None)
        interaction_type = db_object.get("interaction_type", None)
        count = db_object.get("count_", None)
        is_active = db_object.get("is_active", None)

        if audio_key is not None and interaction_type is not None and count is not None and is_active is not None:
            return AudioInteractionCount(
                audio_key=audio_key,
                interaction_type=interaction_type,
                count=count,
                is_active=is_active,
            )

        return None
