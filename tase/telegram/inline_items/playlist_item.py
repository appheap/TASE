from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from .base_inline_item import BaseInlineItem
from ..templates import BaseTemplate, PlaylistData
from ...db import graph_models


class PlaylistItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        db_playlist: graph_models.vertices.Playlist,
        db_from_user: graph_models.vertices.User,
        inline_query: pyrogram.types.InlineQuery,
    ) -> Optional["pyrogram.types.InlineQueryResult"]:
        if db_playlist is None or db_from_user is None:
            return None
        from ..inline_buttons import InlineButton

        data = PlaylistData(
            title=db_playlist.title,
            description=db_playlist.description if db_playlist.description is not None else " ",
            lang_code=db_from_user.chosen_language_code,
        )
        markup = [
            [
                InlineButton.get_button("home").get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                ),
                InlineButton.get_button("back_to_playlists").get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                ),
            ],
            [
                InlineButton.get_button("get_playlist_audios").get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                    db_playlist.key,
                ),
                # todo: add a button to get the top 10 audios from this playlist as a message
            ],
            [
                InlineButton.get_button("edit_playlist_title").get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                    db_playlist.key,
                    callback_arg=db_playlist.key,
                ),
                InlineButton.get_button("edit_playlist_description").get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                    db_playlist.key,
                    callback_arg=db_playlist.key,
                ),
            ],
            [
                InlineButton.get_button("delete_playlist").get_inline_keyboard_button(
                    db_from_user.chosen_language_code,
                    db_playlist.key,
                    callback_arg=db_playlist.key,
                ),
            ],
        ]

        markup = InlineKeyboardMarkup(markup)
        item = InlineQueryResultArticle(
            title=db_playlist.title,
            description=f"{db_playlist.description if db_playlist.description is not None else ' '}",
            id=f"{inline_query.id}->{db_playlist.key}",
            thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg"
            if not db_playlist.is_favorite
            else "https://telegra.ph/file/07d5ca30dba31b5241bcf.jpg",
            input_message_content=InputTextMessageContent(
                message_text=BaseTemplate.registry.playlist_template.render(data),
                parse_mode=ParseMode.HTML,
            ),
            reply_markup=markup,
        )

        return item
