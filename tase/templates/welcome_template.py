from jinja2 import Template

from .base import BaseTemplate, BaseTemplateData
from ..utils import _trans


class WelcomeTemplate(BaseTemplate):
    template = Template(
        "{{c_dir}}{{emoji._headphone}}<b>{{s_title1}}</b>{{emoji._headphone}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{name}}</b>, {{s_welcome_to}} <b>{{s_tase}}</b>. {{s_title_2}}{{emoji._party_popper}}"
        "{{c_new_line}}"
        "{{c_dir}}{{s_title3}} <b>{{s_speed}}</b>{{emoji._zap}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}{{emoji._studio_microphone}} <b>{{s_find}}</b> {{s_title4}} <b>{{s_ms}}</b> {{emoji._smiling_face_with_sunglasses}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}{{emoji._green_circle}} {{s_any_questions}} /help {{emoji._winking_face}}"
    )


class WelcomeData(BaseTemplateData):
    s_title1: str = _trans("Take your audio searching to the speed")
    s_welcome_to: str = _trans("Welcome to")
    s_tase: str = _trans("Telegram Audio Search Engine")
    s_title2: str = _trans("It's great to have you!")
    s_title3: str = _trans("Here are a bunch of features that will get your searching up to")
    s_speed: str = _trans("speed")
    s_find: str = _trans("Find")
    s_title4: str = _trans("your audio (music, podcast, etc.) in")
    s_any_questions: str = _trans("Any question? then press")
    s_ms: str = _trans("milliseconds")

    name: str
