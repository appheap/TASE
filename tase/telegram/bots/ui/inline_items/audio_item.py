import textwrap
from datetime import timedelta, datetime
from typing import Optional, Union

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import InlineQueryResultCachedAudio, InlineQueryResultArticle, InputTextMessageContent

from tase.common.preprocessing import clean_audio_item_text
from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType, InlineQueryType
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.ui.templates import AudioCaptionData, BaseTemplate
from .base_inline_item import BaseInlineItem
from .item_info import AudioItemInfo
from ..base import InlineItemType


class AudioItem(BaseInlineItem):
    __type__ = InlineItemType.AUDIO

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
        inline_query_type: InlineQueryType,
        playlist_key: Optional[str] = None,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if telegram_file_id is None or from_user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        if audio.valid_for_inline_search:
            result_id = AudioItemInfo.parse_id(
                telegram_inline_query,
                hit_download_url,
                inline_query_type,
                audio.valid_for_inline_search,
                chat_type,
                playlist_key,
            )

            from tase.telegram.bots.ui.inline_buttons.common import get_audio_loading_keyboard

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
                reply_markup=get_audio_loading_keyboard(
                    hit_download_url=hit_download_url,
                    lang_code=from_user.chosen_language_code,
                ),
            )
        else:
            return cls.get_article_item(
                bot_username=bot_username,
                from_user=from_user,
                audio=audio,
                telegram_inline_query=telegram_inline_query,
                chats_dict=chats_dict,
                hit_download_url=hit_download_url,
                inline_query_type=inline_query_type,
                playlist_key=playlist_key,
                send_download_url=False,
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
        inline_query_type: InlineQueryType,
        playlist_key: Optional[str] = None,
        send_download_url: bool = True,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if from_user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        result_id = AudioItemInfo.parse_id(
            telegram_inline_query,
            hit_download_url,
            inline_query_type,
            audio.valid_for_inline_search,
            chat_type,
            playlist_key=playlist_key,
        )

        _performer = clean_audio_item_text(audio.raw_performer)
        title = clean_audio_item_text(audio.raw_title)
        _file_name = clean_audio_item_text(
            audio.raw_file_name,
            is_file_name=True,
            remove_file_extension_=True,
        )
        if title is None:
            title = ""
        if _performer is None:
            _performer = ""
        if _file_name is None:
            _file_name = ""

        if not title and _file_name:
            title = _file_name

        if not title:
            title = "   "

        duration = timedelta(seconds=audio.duration or 0)
        d = datetime(1, 1, 1) + duration
        if d.hour:
            _time = f"{d.hour:02}:{d.minute:02}:{d.second:02}"
        else:
            _time = f"{d.minute:02}:{d.second:02}"

        description = (
            f"‎{textwrap.shorten(_performer, 25, placeholder='...')}‎"
            "\n"
            f"{emoji._clock_emoji} {_time:<10}\t"
            f"{emoji._floppy_emoji} {round(audio.file_size / 1_048_576, 1):<6}\t\t"
            f"{emoji._cd} {audio.estimated_bit_rate_type.get_bit_rate_string():<6}"
        )

        if chat_type == ChatType.BOT:
            return InlineQueryResultArticle(
                id=result_id,
                title=f"‎{title}‎",  # todo: set the direction based on the given query.
                description=description,
                thumb_url=audio.get_thumb_telegram_url(),
                input_message_content=InputTextMessageContent(  # todo: add a task to delete this message after the downloaded audio has been sent.
                    f"/dl_{hit_download_url}" if send_download_url else f"{emoji._clock_emoji}",
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML,
                ),
            )
        else:
            from tase.telegram.bots.ui.inline_buttons.common import get_download_audio_keyboard

            return InlineQueryResultArticle(
                id=result_id,
                title=f"‎{title}‎",
                description=description,
                thumb_url=audio.get_thumb_telegram_url(),
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
                reply_markup=get_download_audio_keyboard(
                    bot_username,
                    f"dl_{hit_download_url}",
                    from_user.chosen_language_code,
                ),
            )
