from .button import InlineButton

from ...utils import emoji


class AdvertisementInlineButton(InlineButton):
    name = "advertisement"

    text = f"Advertisement | {emoji._chart_increasing}{emoji._bar_chart}"
    url = "https://t.me/searchify"
