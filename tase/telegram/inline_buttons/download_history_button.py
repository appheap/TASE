import pyrogram
from pyrogram.enums import ChatType
from pyrogram.types import InlineQueryResultCachedAudio, InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup

from tase.telegram.templates import AudioCaptionData
from .button import InlineButton
from .. import template_globals
# from ..handlers import BaseHandler
# from ..inline_buton_globals import buttons
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
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
        from ..inline_buton_globals import buttons  # todo: fix me

        from_ = 0

        if inline_query.offset is not None and len(inline_query.offset):
            from_ = int(inline_query.offset)

        db_audios = db.get_user_download_history(db_from_user, offset=from_)

        results = []

        # todo: fix this
        chats_dict = handler.update_audio_cache(db_audios)

        for db_audio in db_audios:
            db_audio_file_cache = db.get_audio_file_from_cache(db_audio, telegram_client.telegram_id)

            #  todo: Some audios have null titles, solution?
            if not db_audio_file_cache or not db_audio.title:
                continue

            # todo: fix me

            markup = [
                [
                    buttons['add_to_playlist'].get_inline_keyboard_button(
                        db_from_user.chosen_language_code,
                        "db_hit.download_url"
                    ),
                ],

            ]
            if inline_query.chat_type == ChatType.BOT:
                markup.append(
                    [
                        buttons['home'].get_inline_keyboard_button(db_from_user.chosen_language_code),
                    ]
                )

            markup = InlineKeyboardMarkup(markup)

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
                    reply_markup=markup,
                )
            )

        if len(results):
            try:
                next_offset = str(from_ + len(results) + 1) if len(results) else None

                inline_query.answer(results, cache_time=1, next_offset=next_offset)
            except Exception as e:
                logger.exception(e)
        else:
            if from_ is None or from_ == 0:
                inline_query.answer(
                    [
                        InlineQueryResultArticle(
                            title=_trans("No Results Were Found", db_from_user.chosen_language_code),
                            description=_trans(
                                "You haven't downloaded any audios yet",
                                db_from_user.chosen_language_code
                            ),
                            input_message_content=InputTextMessageContent(
                                message_text=emoji.high_voltage,
                            )
                        )
                    ],
                    cache_time=1,
                )
