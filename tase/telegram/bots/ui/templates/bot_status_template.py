from jinja2 import Template

from tase.common.utils import _trans
from .base_template import BaseTemplate, BaseTemplateData


class BotStatusTemplate(BaseTemplate):
    name = "bot_status_template"

    template = Template(
        "{{c_dir}}{{emoji._information}} <b>| {{s_bot_status_title}} |</b> {{emoji._information}}"
        "{{c_new_line}}"
        "{{c_dir}}{{c_sep}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_new_users}}</b>: {{new_users}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_total_users}}</b>: {{total_users}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_new_audios}}</b>: {{new_audios}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_total_audios}}</b>: {{total_audios}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_new_queries}}</b>: {{new_queries}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_total_queries}}</b>: {{total_queries}}"
        "{{c_new_line}}{{c_hidden_char}}"
    )


class BotStatusData(BaseTemplateData):
    s_bot_status_title: str = _trans("Bot Status Information")

    s_new_users: str = _trans("New users")
    s_total_users: str = _trans("Total users")

    s_new_audios: str = _trans("New audio files indexed")
    s_total_audios: str = _trans("Total audio files indexed")

    s_new_queries: str = _trans("New queries")
    s_total_queries: str = _trans("Total queries")

    new_users: str
    total_users: str

    new_audios: str
    total_audios: str

    new_queries: str
    total_queries: str
