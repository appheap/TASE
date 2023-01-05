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
    async def get_status(
        cls,
        db: DatabaseClient,
        from_user: graph_models.vertices.User,
        *,
        hit_download_url: str = None,
        audio_vertex_key: str = None,
    ) -> Optional[AudioKeyboardStatus]:
        if db is None or ((hit_download_url is None or not len(hit_download_url)) and audio_vertex_key is None):
            return None

        from tase.db.arangodb.enums import AudioInteractionType

        valid_for_inline = await db.graph.is_audio_valid_for_inline_mode(
            hit_download_url=hit_download_url,
            audio_vertex_key=audio_vertex_key,
        )

        return AudioKeyboardStatus(
            is_liked=await db.graph.audio_is_interacted_by_user(
                from_user,
                AudioInteractionType.LIKE_AUDIO,
                hit_download_url=hit_download_url,
                audio_vertex_key=audio_vertex_key,
            ),
            is_disliked=await db.graph.audio_is_interacted_by_user(
                from_user,
                AudioInteractionType.DISLIKE_AUDIO,
                hit_download_url=hit_download_url,
                audio_vertex_key=audio_vertex_key,
            ),
            is_in_favorite_playlist=await db.graph.audio_in_favorite_playlist(
                from_user,
                hit_download_url=hit_download_url,
                audio_vertex_key=audio_vertex_key,
            )
            if valid_for_inline
            else None,
        )
