import pyrogram
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup

from .button import InlineButton
# from ..handlers import BaseHandler
from .. import template_globals
from ..telegram_client import TelegramClient
from ..templates import PlaylistData
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import emoji, _trans


class MyPlaylistsInlineButton(InlineButton):
    name = "my_playlists"

    s_my_playlists = _trans("My Playlists")
    text = f"{s_my_playlists} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#my_playlists"

    def on_inline_query(
            self,
            client: 'pyrogram.Client',
            inline_query: 'pyrogram.types.InlineQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
    ):
        from ..inline_buton_globals import buttons

        from_ = 0

        # todo: add `new playlist` button when

        if inline_query.offset is not None and len(inline_query.offset):
            from_ = int(inline_query.offset)

        db_playlists = db.get_user_playlists(db_from_user, offset=from_)

        results = []

        for db_playlist in db_playlists:
            data = PlaylistData(
                title=db_playlist.name,
                description=db_playlist.description,
                lang_code=db_from_user.chosen_language_code,
            )

            markup = [
                [
                    buttons['home'].get_inline_keyboard_button(db_from_user.chosen_language_code),
                    buttons['back'].get_inline_keyboard_button(db_from_user.chosen_language_code),
                ],
                [
                    buttons['get_playlist_audios'].get_inline_keyboard_button(
                        db_from_user.chosen_language_code,
                        db_playlist.key,
                    ),
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
                    title=db_playlist.name,
                    description=f"\n\n{db_playlist.description}",
                    id=f'{inline_query.id}->{db_playlist.id}',
                    thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                    input_message_content=InputTextMessageContent(
                        message_text=template_globals.playlist_template.render(data),
                    ),
                    reply_markup=markup,
                )
            )

        if len(results):
            try:
                # todo: `1` works, but why?
                plus = 1 if inline_query.offset is None or not len(inline_query.offset) else 0
                next_offset = str(from_ + len(results) + plus) if len(results) else None

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
                                "You haven't created any playlist yet",
                                db_from_user.chosen_language_code
                            ),
                            input_message_content=InputTextMessageContent(
                                message_text=emoji.high_voltage,
                            )
                        )
                    ],
                    cache_time=1,
                )
