from __future__ import annotations

from typing import List, Optional

import pyrogram

from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class CreateNewPublicPlaylistItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.CREATE_NEW_PUBLIC_PLAYLIST

    telegram_inline_query_id: str
    item_key: str

    @classmethod
    def parse_id(
        cls,
        telegram_inline_query: pyrogram.types.InlineQuery,
        playlist_key: str,
    ) -> Optional[str]:
        return f"{cls.get_type_value()}|{telegram_inline_query.id}|{playlist_key}"

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[CreateNewPublicPlaylistItemInfo]:
        if len(id_split_lst) != 3:
            return None

        return CreateNewPublicPlaylistItemInfo(
            telegram_inline_query_id=id_split_lst[1],
            item_key=id_split_lst[2],
        )
