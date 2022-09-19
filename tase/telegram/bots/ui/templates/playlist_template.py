from typing import Optional

from jinja2 import Template

from tase.common.utils import _trans
from .base_template import BaseTemplate, BaseTemplateData


class PlaylistTemplate(BaseTemplate):
    name = "playlist_template"

    template = Template(
        "{{c_dir}}<b>{{s_playlist_menu}} |</b> {{emoji._headphone}}"
        "{{c_new_line}}"
        "{{c_dir}}{{c_sep}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_title}}</b>: {{title}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_description}}</b>: {{description}}"
        "{{c_new_line}}{{c_hidden_char}}"
    )


class PlaylistData(BaseTemplateData):
    s_playlist_menu: str = _trans("Playlist Menu")
    s_title: str = _trans("Title")
    s_description: str = _trans("Description")

    title: str
    description: Optional[str] = ""
