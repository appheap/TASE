from .button import InlineButton

from ...utils import emoji, _trans


class AdvertisementInlineButton(InlineButton):
    name = "advertisement"

    s_advertisement = _trans("Advertisement")
    text = f"{s_advertisement} | {emoji._chart_increasing}{emoji._bar_chart}"
    url = "https://t.me/searchify"
