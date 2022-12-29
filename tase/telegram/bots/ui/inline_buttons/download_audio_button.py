from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData


class DownloadAudioButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.DOWNLOAD_AUDIO

    @classmethod
    def generate_data(cls, url: str) -> Optional[str]:
        return url

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return DownloadAudioButtonData()


class DownloadAudioInlineButton(InlineButton):
    __type__ = InlineButtonType.DOWNLOAD_AUDIO
    action = ButtonActionType.OPEN_URL

    s_download_audio = _trans("Download Audio")
    text = f"{s_download_audio} | {emoji._url}"
    url = ""

    @classmethod
    def get_keyboard(
        cls,
        url: str,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            url=DownloadAudioButtonData.generate_data(url),
            lang_code=lang_code,
        )
