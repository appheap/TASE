import random
import textwrap
from typing import Optional

from jinja2 import Template

from tase.static import Emoji
from .base import BaseTemplate, BaseTemplateData
from ..db import elasticsearch_models, graph_models
from ..utils import _trans


class AudioCaptionTemplate(BaseTemplate):
    template = Template(
        "<b>{{s_title}}</b> {{title}} {{c_new_line}}"
        "<b>{{s_performer}}</b> {{performer}} {{c_new_line}}"
        "<b>{{s_file_name}}</b> {{file_name}} {{c_new_line}}"
        "{{emoji._round_pushpin}}{{s_source}} {% if include_source %}{{source}}{%else%}{{s_sent_by_users}}{% endif %}{{c_new_line}}{{c_new_line}}"
        "{{c_dir}}{{emoji._search_emoji}} | <a href='{{bot_url}}'><b>TASE Bot:</b> {{s_audio_search_engine}}</a>{{c_new_line}}"
        "{{c_dir}}{{plant}}"
    )


class AudioCaptionData(BaseTemplateData):
    s_title: str = _trans("Title:")
    s_performer: str = _trans("Performer:")
    s_file_name: str = _trans("File name:")
    s_source: str = _trans("Source:")
    s_audio_search_engine: str = _trans("Audio Search Engine")
    s_sent_by_users: str = _trans('Sent by Telegram Audio Search Engine Users')

    title: str
    performer: str
    file_name: str
    source: str
    include_source: bool
    bot_url: str
    plant: str = random.choice(Emoji().plants_list)

    @staticmethod
    def parse_from_audio_doc(
            audio_doc: elasticsearch_models.Audio,
            user: graph_models.vertices.User,
            chat: graph_models.vertices.Chat,
            bot_url: str,  # todo: get bot_url from config
            include_source: bool = True,  # todo: where to get this variable?
    ) -> Optional['AudioCaptionData']:
        if audio_doc is None or user is None or chat is None or bot_url is None:
            return None

        return AudioCaptionData(
            title=audio_doc.title.replace("@", "") if audio_doc.title else "",
            performer=audio_doc.performer.replace("@", "") if audio_doc.performer else "",
            file_name=textwrap.shorten(
                audio_doc.file_name.replace("@", "") if audio_doc.file_name else "",
                width=40,
                placeholder='...'
            ),
            source=f"<a href ='https://t.me/{chat.username}/{audio_doc.message_id}'>{chat.username}</a>",
            include_source=include_source,
            bot_url=bot_url,

            # todo: fix this
            plant=random.choice(Emoji().plants_list),

            lang_code=user.language_code,
        )
