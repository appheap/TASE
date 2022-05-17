from typing import Optional, Union

import pyrogram.types
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineQueryResultCachedAudio

from .base_inline_item import BaseInlineItem
from .. import template_globals
from ..templates import AudioCaptionData
from ...db import graph_models, document_models, elasticsearch_models


class AudioItem(BaseInlineItem):

    @classmethod
    def get_item(
            cls,
            db_audio_file_cache: document_models.Audio,
            db_from_user: graph_models.vertices.User,
            db_audio: Union[graph_models.vertices.Audio, elasticsearch_models.Audio],
            inline_query: pyrogram.types.InlineQuery,
            chats_dict: dict,
            db_hit: graph_models.vertices.Hit = None,
    ) -> Optional['pyrogram.types.InlineQueryResult']:
        if db_audio_file_cache is None or db_from_user is None:
            return None
        from ..inline_buttons import InlineButton

        markup = [
            [
                InlineButton.get_button('add_to_playlist').get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                    db_hit.download_url if db_hit else "download_url"  # todo: fix me
                ),
            ],

        ]
        if inline_query.chat_type == ChatType.BOT:
            markup.append(
                [
                    InlineButton.get_button('home').get_inline_keyboard_button(db_from_user.chosen_language_code),
                ]
            )

        markup = InlineKeyboardMarkup(markup)

        key = db_audio.key if isinstance(db_audio, graph_models.vertices.Audio) else db_audio.id

        return InlineQueryResultCachedAudio(
            audio_file_id=db_audio_file_cache.file_id,
            id=f'{inline_query.id}->{key}',
            caption=template_globals.audio_caption_template.render(
                AudioCaptionData.parse_from_audio_doc(
                    db_audio,
                    db_from_user,
                    chats_dict[db_audio.chat_id],
                    bot_url='https://t.me/bot?start',
                    include_source=True,
                )
            ),
            reply_markup=markup,
        )
