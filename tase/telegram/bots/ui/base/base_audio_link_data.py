from __future__ import annotations

from typing import Optional, List, Type

from pydantic import BaseModel, Field

from .inline_button_type import InlineButtonType


class BaseAudioLinkData(BaseModel):
    main_type: InlineButtonType = Field(default=InlineButtonType.BASE)
    __button_types__: List[InlineButtonType] = Field(default=[InlineButtonType.BASE])
    __registry__ = dict()

    hit_download_url: str

    @classmethod
    def get_main_type_value(cls) -> int:
        return int(cls.__button_types__[0].value)

    def __init_subclass__(cls, **kwargs):
        for type_ in cls.__button_types__:
            if type_.value in BaseAudioLinkData.__registry__:
                raise ValueError(f"{type_} is already in the registry!")

            BaseAudioLinkData.__registry__[type_.value] = cls

    @classmethod
    def get_button_data(
        cls,
        button_type: InlineButtonType,
    ) -> Optional[Type[BaseAudioLinkData]]:
        if button_type is None or button_type in (
            InlineButtonType.BASE,
            InlineButtonType.UNKNOWN,
            InlineButtonType.INVALID,
        ):
            return None

        return cls.__registry__.get(button_type.value, None)

    @classmethod
    def generate_data(
        cls,
        *args,
        **kwargs,
    ) -> Optional[str]:
        raise NotImplementedError

    @classmethod
    def __parse__(
        cls,
        main_type: InlineButtonType,
        data_split_lst: List[str],
    ) -> Optional[BaseAudioLinkData]:
        raise NotImplementedError

    @classmethod
    def parse_from_string(
        cls,
        data: str,
    ) -> Optional[BaseAudioLinkData]:
        if not data:
            return None

        if not data.startswith("dl_") and "cmd==" not in data:
            return None

        data = data.strip()
        if data.startswith("dl_"):
            button_type_str = str(InlineButtonType.NOT_A_BUTTON.value)
            data_split_lst = data.split("dl_")[1:]
        else:
            _temp = data.split("==")
            button_type_str = _temp[1]
            data_split_lst = _temp[2].split("=")

        if not button_type_str:
            return None

        try:
            button_type_int = int(button_type_str)
        except ValueError:
            return None
        else:
            try:
                button_type = InlineButtonType(button_type_int)
            except ValueError:
                # given button type is not valid
                return None

        if not button_type or button_type in (InlineButtonType.BASE, InlineButtonType.UNKNOWN, InlineButtonType.INVALID):
            return None

        button_data = cls.get_button_data(button_type)
        if not button_data:
            return None

        return button_data.__parse__(button_type, data_split_lst)


class AudioLinkData(BaseAudioLinkData):
    __button_types__ = [
        InlineButtonType.NOT_A_BUTTON,
        InlineButtonType.GET_PLAYLIST_AUDIOS,
    ]

    playlist_key: Optional[str]

    @classmethod
    def generate_data(
        cls,
        hit_download_url: str,
        playlist_key: Optional[str] = None,
        inline_button_type: Optional[InlineButtonType] = InlineButtonType.NOT_A_BUTTON,
    ) -> Optional[str]:
        if inline_button_type == InlineButtonType.NOT_A_BUTTON:
            s_ = f"dl_{hit_download_url}"
        else:
            s_ = f"cmd=={inline_button_type.value}=={hit_download_url}"

        if playlist_key:
            return f"{s_}={playlist_key}"

        return s_

    @classmethod
    def __parse__(
        cls,
        main_type: InlineButtonType,
        data_split_lst: List[str],
    ) -> Optional[AudioLinkData]:
        return AudioLinkData(
            main_type=main_type,
            hit_download_url=data_split_lst[0],
            playlist_key=data_split_lst[1] if len(data_split_lst) > 1 else None,
        )


class DownloadHistoryAudioLinkData(BaseAudioLinkData):
    main_type = InlineButtonType.DOWNLOAD_HISTORY
    __button_types__ = [InlineButtonType.DOWNLOAD_HISTORY]

    @classmethod
    def generate_data(
        cls,
        hit_download_url: str,
    ) -> Optional[str]:
        return f"cmd=={cls.get_main_type_value()}=={hit_download_url}"

    @classmethod
    def __parse__(
        cls,
        main_type: InlineButtonType,
        data_split_lst: List[str],
    ) -> Optional[DownloadHistoryAudioLinkData]:
        return DownloadHistoryAudioLinkData(
            main_type=main_type,
            hit_download_url=data_split_lst[0],
        )
