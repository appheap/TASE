from tase.common.utils import _trans, emoji
from .base import InlineButton, InlineButtonType


class AdvertisementInlineButton(InlineButton):
    name = "advertisement"
    type = InlineButtonType.ADVERTISEMENT

    s_advertisement = _trans("Advertisement")
    text = f"{s_advertisement} | {emoji._chart_increasing}{emoji._bar_chart}"
    url = "https://t.me/advertisement_channel_username"
