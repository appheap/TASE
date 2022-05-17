from typing import Optional

import pyrogram.types
from pyrogram.types import InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent

from .base_inline_item import BaseInlineItem
from .. import template_globals
from ..templates import PlaylistData
from ...db import graph_models


class PlaylistItem(BaseInlineItem):

    @classmethod
    def get_item(
            cls,
            db_playlist: graph_models.vertices.Playlist,
            db_from_user: graph_models.vertices.User,
            inline_query: pyrogram.types.InlineQuery,
    ) -> Optional['pyrogram.types.InlineQueryResult']:
        if db_playlist is None or db_from_user is None:
            return None

        from ..inline_buton_globals import buttons

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
        item = InlineQueryResultArticle(
            title=db_playlist.title,
            description=f"{db_playlist.description}",
            id=f'{inline_query.id}->{db_playlist.key}',
            thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
            input_message_content=InputTextMessageContent(
                message_text=template_globals.playlist_template.render(data),
            ),
            reply_markup=markup,
        )

        return item
