from __future__ import annotations

import random
from typing import Optional, List

import pyrogram

from tase.db.arangodb.enums import ChatType, InlineQueryType
from tase.telegram.bots.ui.base import InlineItemInfo, InlineItemType


class AudioItemInfo(InlineItemInfo):
    __item_type__ = InlineItemType.AUDIO

    telegram_inline_query_id: str
    hit_download_url: str
    chat_type: ChatType
    inline_query_type: InlineQueryType
    random_integer: int
    playlist_key: Optional[str]

    @classmethod
    def parse_id(
        cls,
        telegram_inline_query: pyrogram.types.InlineQuery,
        hit_download_url: str,
        inline_query_type: InlineQueryType,
        chat_type: Optional[ChatType] = None,
        playlist_key: Optional[str] = None,
    ) -> Optional[str]:
        if chat_type is None:
            chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        s_ = f"{cls.get_type_value()}|{telegram_inline_query.id}|{hit_download_url}|{chat_type.value}|{inline_query_type.value}|{random.randint(1, 1_000_000)}"
        if playlist_key:
            return s_ + f"|{playlist_key}"

        return s_

    @classmethod
    def __parse_info__(cls, id_split_lst: List[str]) -> Optional[AudioItemInfo]:
        if len(id_split_lst) < 6:
            return None

        return AudioItemInfo(
            telegram_inline_query_id=id_split_lst[1],
            hit_download_url=id_split_lst[2],
            chat_type=ChatType(int(id_split_lst[3])),
            inline_query_type=InlineQueryType(int(id_split_lst[4])),
            random_integer=int(id_split_lst[5]),
            playlist_key=id_split_lst[6] if len(id_split_lst) > 6 else None,
        )
