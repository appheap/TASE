from typing import Match

import pyrogram
from pyrogram.enums import ChatType
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineQueryResultCachedAudio

from .button import InlineButton
from .. import template_globals
from ..telegram_client import TelegramClient
# from ..handlers import BaseHandler
from ..templates import AudioCaptionData, PlaylistData
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import emoji, _trans


class GetPlaylistAudioInlineButton(InlineButton):
    name = "get_playlist_audios"

    s_audios = _trans("Audios")
    text = f"{s_audios} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#get_playlist_audios"

    def on_inline_query(
            self,
            client: 'pyrogram.Client',
            inline_query: 'pyrogram.types.InlineQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
            reg: Match,
    ):
        from ..inline_buton_globals import buttons  # todo: fix me

        playlist_key = reg.group("arg1")

        from_ = 0
        if inline_query.offset is not None and len(inline_query.offset):
            from_ = int(inline_query.offset)

        results = []

        if from_ == 0:
            db_playlist = db.get_playlist_by_key(playlist_key)
            data = PlaylistData(
                title=db_playlist.title,
                description=db_playlist.description,
                lang_code=db_from_user.chosen_language_code,
            )
            markup = [
                [
                    buttons['home'].get_inline_keyboard_button(db_from_user.chosen_language_code),
                    buttons['back_to_playlists'].get_inline_keyboard_button(db_from_user.chosen_language_code),
                ],
                [
                    buttons['get_playlist_audios'].get_inline_keyboard_button(
                        db_from_user.chosen_language_code,
                        db_playlist.key,
                    ),
                    # todo: add a button to get the top 10 audios from this playlist as a message
                ],
                [
                    buttons['edit_playlist'].get_inline_keyboard_button(
                        db_from_user.chosen_language_code,
                        db_playlist.key,
                    ),
                    buttons['delete_playlist'].get_inline_keyboard_button(
                        db_from_user.chosen_language_code,
                        db_playlist.key,
                    ),
                ],

            ]

            markup = InlineKeyboardMarkup(markup)
            results.append(
                InlineQueryResultArticle(
                    title=db_playlist.title,
                    description=f"{db_playlist.description}",
                    id=f'{inline_query.id}->{db_playlist.id}',
                    thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                    input_message_content=InputTextMessageContent(
                        message_text=template_globals.playlist_template.render(data),
                    ),
                    reply_markup=markup,
                )
            )

        db_audios = db.get_playlist_audios(db_from_user, playlist_key, offset=from_)

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
                if len(results) > 1:
                    next_offset = str(from_ + len(results) + 1) if len(results) else None
                else:
                    next_offset = None

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
