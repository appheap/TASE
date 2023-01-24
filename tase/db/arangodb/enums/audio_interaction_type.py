from __future__ import annotations

from enum import Enum
from typing import Optional


class AudioInteractionType(Enum):
    UNKNOWN = 0

    DOWNLOAD_AUDIO = 1
    REDOWNLOAD_AUDIO = 2
    LIKE_AUDIO = 3
    DISLIKE_AUDIO = 4
    SHARE_AUDIO = 5
    SHARE_AUDIO_LINK = 6

    # Audio interaction vertices with the following values are also connected to playlist vertices.
    ADD_TO_PRIVATE_PLAYLIST = 51
    ADD_TO_PUBLIC_PLAYLIST = 52
    ADD_TO_FAVORITE_PLAYLIST = 53

    @staticmethod
    def interaction_has_playlist(interaction_type: AudioInteractionType) -> Optional[bool]:
        if not interaction_type:
            return None

        if interaction_type in (
            AudioInteractionType.ADD_TO_PRIVATE_PLAYLIST,
            AudioInteractionType.ADD_TO_PUBLIC_PLAYLIST,
            AudioInteractionType.ADD_TO_FAVORITE_PLAYLIST,
        ):
            return True

        return False
