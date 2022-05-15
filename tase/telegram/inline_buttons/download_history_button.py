import pyrogram
from pyrogram.types import InlineQueryResultCachedAudio, InlineQueryResultArticle, InputTextMessageContent

from .button import InlineButton
from .. import template_globals
from ..telegram_client import TelegramClient
from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from tase.telegram.templates import AudioCaptionData
from ...utils import emoji, _trans


class DownloadHistoryInlineButton(InlineButton):
    name = "download_history"

    s_my_downloads = _trans("My Downloads")
    text = f"{s_my_downloads} | {emoji._mobile_phone_with_arrow}"

    switch_inline_query_current_chat = f"#download_history"

    def on_inline_query(
            self,
            client: 'pyrogram.Client',
            inline_query: 'pyrogram.types.InlineQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
    ):
        db_audios = db.get_user_download_history(db_from_user)

        results = []

        # todo: fix this
        chats_dict = handler.update_audio_cache(db_audios)

        for db_audio in db_audios:
            db_audio_file_cache = db.get_audio_file_from_cache(db_audio, telegram_client.telegram_id)

            #  todo: Some audios have null titles, solution?
            if not db_audio_file_cache or not db_audio.title:
                continue

            results.append(
                InlineQueryResultCachedAudio(
                    audio_file_id=db_audio_file_cache.file_id,
                    id=f'{inline_query.id}->{db_audio.key}',
                    caption=template_globals.audio_caption_template.render(
                        AudioCaptionData.parse_from_audio_doc(
                            db_audio,
                            db_from_user,
                            chats_dict[db_audio.chat_id],
                            bot_url='https://t.me/bot?start',
                            include_source=True,
                        )
                    ),
                )
            )

        if len(results):
            try:
                # inline_query.answer(results, cache_time=1, next_offset=next_offset)
                inline_query.answer(results, cache_time=1)
            except Exception as e:
                logger.exception(e)
        else:
            inline_query.answer(
                [
                    InlineQueryResultArticle(
                        title="No Results",
                        description="You haven't downloaded any audios yet",
                        input_message_content=InputTextMessageContent(
                            message_text=emoji.high_voltage,
                        )
                    )
                ]
            )
