from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel

from .inline_item_type import InlineItemType


class InlineItemInfo(BaseModel):
    __item_type__: InlineItemType

    @property
    def type(self) -> InlineItemType:
        return self.__item_type__

    @classmethod
    def get_type_value(cls) -> int:
        return cls.__item_type__.value

    @classmethod
    def parse_id(cls, *args, **kwargs) -> Optional[str]:
        raise f"{cls.get_type_value()}|"

    @classmethod
    def __parse_info__(
        cls,
        id_split_lst: List[str],
    ) -> Optional[InlineItemInfo]:
        raise NotImplementedError

    @classmethod
    def get_info(
        cls,
        id_: str,
    ) -> Optional[InlineItemInfo]:
        if not id_ or "|" not in id_:
            return None

        id_split_lst = id_.split("|")
        item_type_str = id_split_lst[0]
        if not item_type_str:
            return None

        from tase.telegram.bots.ui.inline_items.item_info import (
            AudioInNoPlaylistInfo,
            AudioItemInfo,
            CreateNewPrivatePlaylistItemInfo,
            CreateNewPublicPlaylistItemInfo,
            NoDownloadItemInfo,
            NoPlaylistItemInfo,
            NoResultItemInfo,
            PlaylistItemInfo,
        )

        item_type = InlineItemType(int(item_type_str))

        if item_type == InlineItemType.AUDIO_IN_NO_PLAYLIST:
            obj = AudioInNoPlaylistInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.AUDIO:
            obj = AudioItemInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.CREATE_NEW_PRIVATE_PLAYLIST:
            obj = CreateNewPrivatePlaylistItemInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.CREATE_NEW_PUBLIC_PLAYLIST:
            obj = CreateNewPublicPlaylistItemInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.NO_DOWNLOAD:
            obj = NoDownloadItemInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.NO_PLAYLIST:
            obj = NoPlaylistItemInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.NO_RESULT:
            obj = NoResultItemInfo.__parse_info__(id_split_lst)

        elif item_type == InlineItemType.PLAYLIST:
            obj = PlaylistItemInfo.__parse_info__(id_split_lst)

        else:
            obj = None

        return obj
