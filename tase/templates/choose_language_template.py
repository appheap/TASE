from jinja2 import Template

from .base import BaseTemplate, BaseTemplateData
from ..utils import _trans


class ChooseLanguageTemplate(BaseTemplate):
    template = Template(
        "<b>{{s_choose_your_language}} {{name}} |</b> {{emoji._globe_showing_Americas}} {{c_new_line}}{{c_new_line}}"
        "{{s_change_later}}{{c_new_line}}"
        "   1. {{s_sending}} <b>/lang</b>{{c_new_line}}"
        "   2. {{s_go_to}} <b>{{s_home}} | {{emoji._house}}</b>{{c_new_line}} {{c_hidden_char}}"
    )


class ChooseLanguageData(BaseTemplateData):
    s_choose_your_language: str = _trans("Please choose your language")
    s_change_later: str = _trans("You can change this later by:")
    s_sending: str = _trans("Sending")
    s_go_to: str = _trans("Going to")
    s_home: str = _trans("Home")

    name: str
