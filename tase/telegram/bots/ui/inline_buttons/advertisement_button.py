from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData


class AdvertisementButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.ADVERTISEMENT

    url: str

    @classmethod
    def generate_data(cls, url: str) -> Optional[str]:
        return url

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return AdvertisementButtonData(url=data_split_lst[1])


class AdvertisementInlineButton(InlineButton):
    __type__ = InlineButtonType.ADVERTISEMENT
    action = ButtonActionType.OPEN_URL

    s_advertisement = _trans("Advertisement")
    text = f"{s_advertisement} | {emoji._chart_increasing}{emoji._bar_chart}"
    url = "https://t.me/advertisement_channel_username"

    @classmethod
    def get_keyboard(
        cls,
        url: Optional[str] = None,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        btn = cls.get_button(cls.__type__)

        return btn.__parse_keyboard_button__(
            url=AdvertisementButtonData.generate_data(url if url else btn.url),
            lang_code=lang_code,
        )
