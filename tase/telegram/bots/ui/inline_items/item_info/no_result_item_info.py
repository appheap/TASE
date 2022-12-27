from __future__ import annotations

from typing import Optional, List

from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class NoResultItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.NO_RESULT

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[NoResultItemInfo]:
        return NoResultItemInfo()
