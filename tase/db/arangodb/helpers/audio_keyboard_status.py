from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from tase.db import DatabaseClient
    from tase.db.arangodb import graph as graph_models


class AudioKeyboardStatus(BaseModel):
    is_liked: bool
    is_disliked: bool
    is_in_favorite_playlist: Optional[bool]

    @classmethod
    def get_status(
        cls,
        db: DatabaseClient,
        from_user: graph_models.vertices.User,
        hit_download_url: str,
    ) -> Optional[AudioKeyboardStatus]:
        if db is None:
            return None

        from tase.db.arangodb.enums import InteractionType

        valid_for_inline = db.graph.is_audio_valid_for_inline_mode(hit_download_url)

        return AudioKeyboardStatus(
            is_liked=db.graph.audio_is_interacted_by_user(
                from_user,
                hit_download_url,
                InteractionType.LIKE,
            ),
            is_disliked=db.graph.audio_is_interacted_by_user(
                from_user,
                hit_download_url,
                InteractionType.DISLIKE,
            ),
            is_in_favorite_playlist=db.graph.audio_in_favorite_playlist(
                from_user,
                hit_download_url,
            )
            if valid_for_inline
            else None,
        )
