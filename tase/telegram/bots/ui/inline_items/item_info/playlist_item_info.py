from __future__ import annotations

from typing import Optional, List

import pyrogram

from tase.db.arangodb.enums import ChatType
from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class PlaylistItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.PLAYLIST

    telegram_inline_query_id: str
    playlist_key: str
    chat_type: ChatType
    hit_download_url: Optional[str]

    @classmethod
    def parse_id(
        cls,
        telegram_inline_query: pyrogram.types.InlineQuery,
        playlist_key: str,
        chat_type: Optional[ChatType] = None,
        hit_download_url: Optional[str] = None,
    ) -> Optional[str]:
        if chat_type is None:
            chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        _s = f"{cls.get_type_value()}|{telegram_inline_query.id}|{playlist_key}|{chat_type.value}"
        if hit_download_url:
            return _s + f"|{hit_download_url}"
        else:
            return _s

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[PlaylistItemInfo]:
        if len(id_split_lst) < 4:
            return None

        return PlaylistItemInfo(
            telegram_inline_query_id=id_split_lst[1],
            playlist_key=id_split_lst[2],
            chat_type=ChatType(int(id_split_lst[3])),
            hit_download_url=id_split_lst[4] if len(id_split_lst) > 4 else None,
        )
