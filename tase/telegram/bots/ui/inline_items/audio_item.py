from typing import Optional

import pyrogram.types
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineQueryResultCachedAudio

from tase.db.arangodb import graph as graph_models
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.ui.templates import AudioCaptionData, BaseTemplate
from .base_inline_item import BaseInlineItem


class AudioItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        telegram_file_id: str,
        from_user: graph_models.vertices.User,
        es_audio_doc: elasticsearch_models.Audio,
        telegram_inline_query: pyrogram.types.InlineQuery,
        chats_dict: dict,
        hit: graph_models.vertices.Hit,
    ) -> Optional["pyrogram.types.InlineQueryResult"]:
        if telegram_file_id is None or from_user is None:
            return None

        from ..inline_buttons import InlineButton

        markup = [
            [
                InlineButton.get_button("add_to_playlist").get_inline_keyboard_button(
                    from_user.chosen_language_code,
                    hit.download_url,
                ),
            ],
            [
                InlineButton.get_button(
                    "remove_from_playlist"
                ).get_inline_keyboard_button(
                    from_user.chosen_language_code,
                    hit.download_url,
                ),
            ],
        ]
        if telegram_inline_query.chat_type == ChatType.BOT:
            markup.append(
                [
                    InlineButton.get_button("home").get_inline_keyboard_button(
                        from_user.chosen_language_code
                    ),
                ]
            )

        markup = InlineKeyboardMarkup(markup)

        return InlineQueryResultCachedAudio(
            audio_file_id=telegram_file_id,
            id=f"{telegram_inline_query.id}->{hit.download_url}",
            caption=BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_es_audio_doc(
                    es_audio_doc,
                    from_user,
                    chats_dict[es_audio_doc.chat_id],
                    bot_url="https://t.me/bot?start",
                    include_source=True,
                )
            ),
            reply_markup=markup,
        )
