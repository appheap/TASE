from __future__ import annotations

from typing import List, Optional

from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class NoDownloadItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.NO_DOWNLOAD

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[NoDownloadItemInfo]:
        return NoDownloadItemInfo()
