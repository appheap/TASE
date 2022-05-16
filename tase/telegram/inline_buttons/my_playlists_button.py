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

        if from_ == 0:
            results.append(
                InlineQueryResultArticle(
                    title=_trans("Create A New Playlist", db_from_user.chosen_language_code),
                    description=_trans("Create a new playlist", db_from_user.chosen_language_code),
                    id=f'{inline_query.id}->add_a_new_playlist',
                    thumb_url="https://telegra.ph/file/aaafdf705c6745e1a32ee.png",
                    input_message_content=InputTextMessageContent(message_text=emoji._clock_emoji),
                )
            )

        for db_playlist in db_playlists:
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
                    id=f'{inline_query.id}->{db_playlist.key}',
                    thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                    input_message_content=InputTextMessageContent(
                        message_text=template_globals.playlist_template.render(data),
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

    def on_chosen_inline_query(
            self,
            client: 'pyrogram.Client',
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User
    ):
        res = chosen_inline_result.query.split(" ")
        try:
            hit_download_url = res[1]
        except:
            hit_download_url = None

        result_id_list = chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]

        # db_hit = db.get_hit_by_download_url(hit_download_url)
        # db_audio = db.get_audio_from_hit(db_hit)

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            pass
