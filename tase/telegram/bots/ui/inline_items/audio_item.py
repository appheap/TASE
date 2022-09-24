from typing import Optional

import pyrogram.types
from pyrogram.types import InlineKeyboardMarkup, InlineQueryResultCachedAudio

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
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
        audio_in_favorite_playlist: bool,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if telegram_file_id is None or from_user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        from tase.telegram.bots.ui.inline_buttons.base import (
            InlineButton,
            InlineButtonType,
        )

        markup = [
            [
                InlineButton.get_button(
                    InlineButtonType.ADD_TO_PLAYLIST
                ).get_inline_keyboard_button(
                    from_user.chosen_language_code,
                    hit.download_url,
                ),
                InlineButton.get_button(
                    InlineButtonType.REMOVE_FROM_PLAYLIST
                ).get_inline_keyboard_button(
                    from_user.chosen_language_code,
                    hit.download_url,
                ),
                InlineButton.get_button(InlineButtonType.ADD_TO_FAVORITE_PLAYLIST)
                .change_text(audio_in_favorite_playlist)
                .get_inline_keyboard_button(
                    from_user.chosen_language_code,
                    callback_arg=hit.download_url,
                ),
            ],
        ]
        if chat_type == ChatType.BOT:
            markup.append(
                [
                    InlineButton.get_button(
                        InlineButtonType.HOME
                    ).get_inline_keyboard_button(
                        from_user.chosen_language_code,
                        chat_type=chat_type,
                    ),
                ]
            )

        return InlineQueryResultCachedAudio(
            audio_file_id=telegram_file_id,
            id=f"{telegram_inline_query.id}->{hit.download_url}->{chat_type.value}",
            caption=BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_es_audio_doc(
                    es_audio_doc,
                    from_user,
                    chats_dict[es_audio_doc.chat_id],
                    bot_url="https://t.me/bot?start",
                    include_source=True,
                )
            ),
            reply_markup=InlineKeyboardMarkup(markup),
        )
