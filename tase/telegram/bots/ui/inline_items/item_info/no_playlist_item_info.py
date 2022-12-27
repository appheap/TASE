from __future__ import annotations

from typing import Optional, List

from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class NoPlaylistItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.NO_PLAYLIST

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[NoPlaylistItemInfo]:
        return NoPlaylistItemInfo()
