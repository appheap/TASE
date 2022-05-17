from jinja2 import Template

from .base_template import BaseTemplate, BaseTemplateData
from tase.utils import _trans


class HomeTemplate(BaseTemplate):
    name = "home_template"

    template = Template(
        "{{c_dir}}<b>{{s_main_menu}} | {{emoji._house}}</b>"
        "{{c_new_line}}"
        "{{c_dir}}{{c_sep}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}{{s_our_channels}}"
        "{{c_new_line}}"
        "{{c_dir}}{{s_channel}} <b>@{{support_channel_username}}</b> | {{emoji._pushpin}}"
        "{{c_new_line}}"
        "{{c_dir}}{{c_sep}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}{{s_contact_us}}"
        "{{c_new_line}}"
        "{{c_dir}}<a href='{{url1}}'>{{s_tase}}</a> | {{emoji._round_pushpin}}"
        "{{c_new_line}}"
        "{{c_dir}}<a href='{{url2}}'>{{s_tase}}</a> | {{emoji._round_pushpin}}"
        "{{c_new_line}}"
        "{{emoji._plant}}{{emoji._heart}}"
    )


class HomeData(BaseTemplateData):
    s_main_menu: str = _trans("Main menu")
    s_channel: str = _trans("Channel:")
    s_our_channels: str = _trans("Our channels:")
    s_tase: str = _trans("Telegram Audio Search Engine")
    s_contact_us: str = _trans("How to reach us:")

    support_channel_username: str
    url1: str
    url2: str
