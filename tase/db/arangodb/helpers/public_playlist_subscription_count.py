from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PublicPlaylistSubscriptionCount(BaseModel):
    playlist_key: str
    count: int
    is_active: bool

    @classmethod
    def parse(
        cls,
        db_object: dict,
    ) -> Optional[PublicPlaylistSubscriptionCount]:
        if db_object is None or not len(db_object):
            return None

        playlist_key = db_object.get("playlist_key", None)
        count = db_object.get("count_", None)
        is_active = db_object.get("is_active", None)

        if playlist_key is not None and count is not None and is_active is not None:
            return PublicPlaylistSubscriptionCount(
                playlist_key=playlist_key,
                count=count,
                is_active=is_active,
            )

        return None
