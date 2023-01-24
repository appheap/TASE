from __future__ import annotations

from typing import Optional, List

import pyrogram

from tase.db.arangodb.enums import ChatType
from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class PlaylistItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.PLAYLIST

    telegram_inline_query_id: str
    playlist_key: str
    is_public: bool
    chat_type: ChatType
    playlist_hit_download_url: Optional[str]

    @classmethod
    def parse_id(
        cls,
        telegram_inline_query: pyrogram.types.InlineQuery,
        playlist_key: str,
        is_public: bool,
        chat_type: Optional[ChatType] = None,
        playlist_hit_download_url: Optional[str] = None,
    ) -> Optional[str]:
        if chat_type is None:
            chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        _s = f"{cls.get_type_value()}|{telegram_inline_query.id}|{playlist_key}|{int(is_public)}|{chat_type.value}"
        if playlist_hit_download_url:
            return _s + f"|{playlist_hit_download_url}"
        else:
            return _s

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[PlaylistItemInfo]:
        if len(id_split_lst) < 5:
            return None

        return PlaylistItemInfo(
            telegram_inline_query_id=id_split_lst[1],
            playlist_key=id_split_lst[2],
            is_public=bool(int(id_split_lst[3])),
            chat_type=ChatType(int(id_split_lst[4])),
            playlist_hit_download_url=id_split_lst[5] if len(id_split_lst) > 5 else None,
        )
