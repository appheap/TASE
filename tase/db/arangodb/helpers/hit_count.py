from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from tase.db.arangodb.enums import HitType


class HitCount(BaseModel):
    audio_key: str
    hit_type: HitType
    count: int

    @classmethod
    def parse(
        cls,
        db_object: dict,
    ) -> Optional[HitCount]:
        if db_object is None or not len(db_object):
            return None

        audio_key = db_object.get("audio_key", None)
        hit_type = db_object.get("hit_type", None)
        count = db_object.get("count_", None)

        if audio_key is not None and hit_type is not None and count is not None:
            return HitCount(
                audio_key=audio_key,
                hit_type=hit_type,
                count=count,
            )

        return None
