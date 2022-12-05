from __future__ import annotations

import textwrap
from typing import Optional, Union

from jinja2 import Template

from tase.common.preprocessing import clean_audio_item_text
from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.db.elasticsearchdb import models as elasticsearch_models
from .base_template import BaseTemplate, BaseTemplateData


class AudioCaptionTemplate(BaseTemplate):
    name = "audio_caption_template"

    template = Template(
        "{{c_dir}}<b>{{s_title}}:</b> {{title}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_performer}}:</b> {{performer}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_file_name}}:</b> {{file_name}}"
        "{{c_new_line}}"
        "{{c_dir}}<b>{{s_quality}}:</b> ~{{quality_string}}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}{{emoji._round_pushpin}}{{s_source}}: {% if include_source %}{{source}}{%else%}{{s_sent_by_users}}{% endif %}"
        "{{c_new_line}}"
        "{{c_new_line}}"
        "{{c_dir}}{{emoji._search_emoji}} | <a href='{{bot_url}}'><b>TASE Bot:</b> {{s_audio_search_engine}}</a>"
        "{{c_new_line}}"
    )


class AudioCaptionData(BaseTemplateData):
    s_title: str = _trans("Title")
    s_performer: str = _trans("Performer")
    s_file_name: str = _trans("File name")
    s_source: str = _trans("Source")
    s_quality: str = _trans("Quality")
    s_audio_search_engine: str = _trans("Audio Search Engine")
    s_sent_by_users: str = _trans("Submitted by Telegram Audio Search Engine Users")

    title: Optional[str]
    performer: Optional[str]
    file_name: Optional[str]
    source: str
    include_source: bool
    bot_url: str
    quality_string: str

    @staticmethod
    def parse_from_audio(
        audio: Union[elasticsearch_models.Audio, graph_models.vertices.Audio],
        user: graph_models.vertices.User,
        chat: graph_models.vertices.Chat,
        bot_url: str,  # todo: get bot_url from config
        include_source: bool = True,  # todo: where to get this variable?
    ) -> Optional[AudioCaptionData]:
        if audio is None or user is None or chat is None or bot_url is None:
            return None

        return AudioCaptionData(
            title=clean_audio_item_text(audio.raw_title),
            performer=clean_audio_item_text(audio.raw_performer),
            file_name=textwrap.shorten(
                clean_audio_item_text(audio.raw_file_name, is_file_name=True),
                width=40,
                placeholder="...",
            ),
            source=f"<a href ='https://t.me/{chat.username}/{audio.message_id}'>{chat.username}</a>",
            include_source=include_source,
            bot_url=bot_url,
            quality_string=audio.estimated_bit_rate_type.get_bit_rate_string(True),
            lang_code=user.chosen_language_code,
        )
