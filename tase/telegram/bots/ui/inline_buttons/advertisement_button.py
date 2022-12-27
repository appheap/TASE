from tase.common.utils import _trans, emoji
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType


class AdvertisementInlineButton(InlineButton):
    type = InlineButtonType.ADVERTISEMENT
    action = ButtonActionType.OPEN_URL

    s_advertisement = _trans("Advertisement")
    text = f"{s_advertisement} | {emoji._chart_increasing}{emoji._bar_chart}"
    url = "https://t.me/advertisement_channel_username"
