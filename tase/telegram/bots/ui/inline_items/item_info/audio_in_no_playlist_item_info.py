from __future__ import annotations

from typing import List, Optional

from tase.telegram.bots.ui.base import InlineItemType, InlineItemInfo


class AudioInNoPlaylistInfo(InlineItemInfo):
    __item_type__ = InlineItemType.AUDIO_IN_NO_PLAYLIST

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[AudioInNoPlaylistInfo]:
        return AudioInNoPlaylistInfo()
