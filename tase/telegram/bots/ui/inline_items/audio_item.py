import random
from typing import Optional, Union

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultCachedAudio, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent

from tase.common.preprocessing import clean_audio_item_text
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

    @classmethod
    def get_article_item(
        cls,
        bot_username: str,
        from_user: graph_models.vertices.User,
        audio: Union[elasticsearch_models.Audio, graph_models.vertices.Audio],
        telegram_inline_query: pyrogram.types.InlineQuery,
        chats_dict: dict,
        hit_download_url: str,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if from_user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        result_id = cls.parse_id(
            telegram_inline_query,
            hit_download_url,
            chat_type,
        )

        if chat_type == ChatType.BOT:
            return InlineQueryResultArticle(
                id=result_id,
                title=clean_audio_item_text(audio.raw_title) or "None",  # fixme
                description=clean_audio_item_text(audio.raw_performer),
                thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                input_message_content=InputTextMessageContent(  # todo: add a task to delete this message after the downloaded audio has been sent.
                    f"/dl_{hit_download_url}",
                    disable_web_page_preview=True,
                ),
            )
        else:
            return InlineQueryResultArticle(
                id=result_id,
                title=clean_audio_item_text(audio.raw_title) or "None",  # fixme
                description=clean_audio_item_text(audio.raw_performer),
                thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                input_message_content=InputTextMessageContent(
                    BaseTemplate.registry.audio_caption_template.render(
                        AudioCaptionData.parse_from_audio(
                            audio,
                            from_user,
                            chats_dict[audio.chat_id],
                            bot_url=f"https://t.me/{bot_username}?start=dl_{hit_download_url}",
                            include_source=False,
                            show_source=False,
                        ),
                    ),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineButton.get_button(InlineButtonType.DOWNLOAD_AUDIO).get_inline_keyboard_button(
                                from_user.chosen_language_code,
                                url=f"https://t.me/{bot_username}?start=dl_{hit_download_url}",
                            ),
                        ]
                    ]
                ),
            )
