import random
from typing import Optional, Union

import pyrogram.types
from pyrogram.types import InlineQueryResultCachedAudio, InlineKeyboardMarkup

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.ui.templates import AudioCaptionData, BaseTemplate
from .base_inline_item import BaseInlineItem
from ..inline_buttons.base import InlineButton, InlineButtonType


class AudioItem(BaseInlineItem):
    @classmethod
    def parse_id(
        cls,
        telegram_inline_query: pyrogram.types.InlineQuery,
        hit_download_url: str,
        chat_type: Optional[ChatType] = None,
    ) -> Optional[str]:
        if chat_type is None:
            chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)
        return f"{telegram_inline_query.id}->{hit_download_url}->{chat_type.value}->{random.randint(1, 1_000_000)}"

    @classmethod
    def get_item(
        cls,
        bot_username: str,
        telegram_file_id: str,
        from_user: graph_models.vertices.User,
        audio: Union[elasticsearch_models.Audio, graph_models.vertices.Audio],
        telegram_inline_query: pyrogram.types.InlineQuery,
        chats_dict: dict,
        hit_download_url: str,
        status: Optional[AudioKeyboardStatus] = None,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if telegram_file_id is None or from_user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        result_id = cls.parse_id(
            telegram_inline_query,
            hit_download_url,
            chat_type,
        )

        # return InlineQueryResultArticle(
        #     id=result_id,
        #     title=audio.title,
        #     description=audio.message_caption,
        #     thumb_url="https://telegra.ph/file/d15b185d0154fc8a92210.jpg",
        #         input_message_content=InputTextMessageContent(f"/dl_{hit_download_url}"),
        # input_message_content=InputTextMessageContent(
        #     BaseTemplate.registry.audio_caption_template.render(
        #         AudioCaptionData.parse_from_audio(
        #             audio,
        #             from_user,
        #             chats_dict[audio.chat_id],
        #             bot_url=f"https://t.me/{bot_username}?start=dl_{hit_download_url}",
        #             include_source=True,
        #         ),
        #     ),
        #     parse_mode=ParseMode.HTML,
        # ),
        # reply_markup=get_audio_markup_keyboard(
        #     bot_username,
        #     chat_type,
        #     from_user.chosen_language_code,
        #     hit_download_url,
        #     audio.valid_for_inline_search,
        #     status,
        # ),
        # )

        return InlineQueryResultCachedAudio(
            audio_file_id=telegram_file_id,
            id=result_id,
            caption=BaseTemplate.registry.audio_caption_template.render(
                AudioCaptionData.parse_from_audio(
                    audio,
                    from_user,
                    chats_dict[audio.chat_id],
                    bot_url=f"https://t.me/{bot_username}?start=dl_{hit_download_url}",
                    include_source=True,
                )
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineButton.get_button(InlineButtonType.LOADING_KEYBOARD).get_inline_keyboard_button(
                            from_user.chosen_language_code,
                        ),
                    ]
                ]
            ),
        )
