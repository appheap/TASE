from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.templates import BaseTemplate, PlaylistData
from .base_inline_item import BaseInlineItem


class PlaylistItem(BaseInlineItem):
    @classmethod
    def get_item(
        cls,
        playlist: graph_models.vertices.Playlist,
        user: graph_models.vertices.User,
        telegram_inline_query: pyrogram.types.InlineQuery,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if playlist is None or user is None:
            return None

        data = PlaylistData(
            title=playlist.title,
            description=playlist.description
            if playlist.description is not None
            else " ",
            lang_code=user.chosen_language_code,
        )
        from tase.telegram.bots.ui.inline_buttons.base import (
            InlineButton,
            InlineButtonType,
        )

        if playlist.is_favorite:
            markup = [
                [
                    InlineButton.get_button(
                        InlineButtonType.GET_PLAYLIST_AUDIOS
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                        playlist.key,
                    ),
                    # todo: add a button to get the top 10 audios from this playlist as a message
                ],
                [
                    InlineButton.get_button(
                        InlineButtonType.HOME
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                    ),
                    InlineButton.get_button(
                        InlineButtonType.BACK_TO_PLAYLISTS
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                    ),
                ],
            ]
        else:
            markup = [
                [
                    InlineButton.get_button(
                        InlineButtonType.HOME
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                    ),
                    InlineButton.get_button(
                        InlineButtonType.BACK_TO_PLAYLISTS
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                    ),
                ],
                [
                    InlineButton.get_button(
                        InlineButtonType.GET_PLAYLIST_AUDIOS
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                        playlist.key,
                    ),
                    # todo: add a button to get the top 10 audios from this playlist as a message
                ],
                [
                    InlineButton.get_button(
                        InlineButtonType.EDIT_PLAYLIST_TITLE
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                        playlist.key,
                        callback_arg=playlist.key,
                    ),
                    InlineButton.get_button(
                        InlineButtonType.EDIT_PLAYLIST_DESCRIPTION
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                        playlist.key,
                        callback_arg=playlist.key,
                    ),
                ],
                [
                    InlineButton.get_button(
                        InlineButtonType.DELETE_PLAYLIST
                    ).get_inline_keyboard_button(
                        user.chosen_language_code,
                        playlist.key,
                        callback_arg=playlist.key,
                    ),
                ],
            ]

        markup = InlineKeyboardMarkup(markup)
        item = InlineQueryResultArticle(
            title=playlist.title,
            description=f"{playlist.description if playlist.description is not None else ' '}",
            id=f"{telegram_inline_query.id}->{playlist.key}",
            thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg"
            if not playlist.is_favorite
            else "https://telegra.ph/file/07d5ca30dba31b5241bcf.jpg",
            input_message_content=InputTextMessageContent(
                message_text=BaseTemplate.registry.playlist_template.render(data),
                parse_mode=ParseMode.HTML,
            ),
            reply_markup=markup,
        )

        return item
