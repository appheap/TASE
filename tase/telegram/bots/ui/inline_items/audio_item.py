import random
from typing import Optional

import pyrogram.types
from pyrogram.types import InlineQueryResultCachedAudio

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.ui.templates import AudioCaptionData, BaseTemplate
from .base_inline_item import BaseInlineItem


class AudioItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        bot_username: str,
        telegram_file_id: str,
        from_user: graph_models.vertices.User,
        es_audio_doc: elasticsearch_models.Audio,
        telegram_inline_query: pyrogram.types.InlineQuery,
        chats_dict: dict,
        hit: graph_models.vertices.Hit,
        audio_in_favorite_playlist: bool,
        audio_is_disliked: bool,
        audio_is_liked: bool,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if telegram_file_id is None or from_user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        from tase.telegram.bots.ui.inline_buttons.common import (
            get_audio_markup_keyboard,
        )

        return InlineQueryResultCachedAudio(
            audio_file_id=telegram_file_id,
            id=f"{telegram_inline_query.id}->{hit.download_url}->{chat_type.value}->{random.randint(1, 1_000_000)}",
            caption=BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_es_audio_doc(
                    es_audio_doc,
                    from_user,
                    chats_dict[es_audio_doc.chat_id],
                    bot_url=f"https://t.me/{bot_username}?start=dl_{hit.download_url}",
                    include_source=True,
                )
            ),
            reply_markup=get_audio_markup_keyboard(
                bot_username,
                chat_type,
                from_user.chosen_language_code,
                hit.download_url,
                es_audio_doc.valid_for_inline_search,
                audio_in_favorite_playlist,
                audio_is_disliked,
                audio_is_liked,
            ),
        )
