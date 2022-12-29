from typing import Optional

import pyrogram.types
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.ui.base import InlineItemType
from tase.telegram.bots.ui.templates import BaseTemplate, PlaylistData
from .base_inline_item import BaseInlineItem


class PlaylistItem(BaseInlineItem):
    __type__ = InlineItemType.PLAYLIST

    @classmethod
    def get_item(
        cls,
        playlist: graph_models.vertices.Playlist,
        user: graph_models.vertices.User,
        telegram_inline_query: pyrogram.types.InlineQuery,
        view_playlist: Optional[bool] = True,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if playlist is None or user is None:
            return None

        from tase.telegram.bots.ui.inline_items.item_info import PlaylistItemInfo

        if view_playlist:
            data = PlaylistData(
                title=playlist.title,
                description=playlist.description if playlist.description is not None else " ",
                lang_code=user.chosen_language_code,
            )

            from tase.telegram.bots.ui.inline_buttons.common import get_playlist_markup_keyboard

            return InlineQueryResultArticle(
                title=playlist.title,
                description=f"{playlist.description if playlist.description is not None else ' '}",
                id=PlaylistItemInfo.parse_id(telegram_inline_query, playlist.key, ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)),
                thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg"
                if not playlist.is_favorite
                else "https://telegra.ph/file/07d5ca30dba31b5241bcf.jpg",
                input_message_content=InputTextMessageContent(
                    message_text=BaseTemplate.registry.playlist_template.render(data),
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=get_playlist_markup_keyboard(
                    playlist,
                    user.chosen_language_code,
                ),
            )
        else:
            return InlineQueryResultArticle(
                title=playlist.title,
                description=f"{playlist.description if playlist.description is not None else ' '}",
                id=PlaylistItemInfo.parse_id(telegram_inline_query, playlist.key, ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)),
                thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg"
                if not playlist.is_favorite
                else "https://telegra.ph/file/07d5ca30dba31b5241bcf.jpg",
                input_message_content=InputTextMessageContent(
                    message_text=emoji._clock_emoji,
                    parse_mode=ParseMode.HTML,
                ),
            )

    @classmethod
    def get_item_from_es_doc(
        cls,
        playlist: elasticsearch_models.Playlist,
        user: graph_models.vertices.User,
        telegram_inline_query: pyrogram.types.InlineQuery,
        view_playlist: Optional[bool] = True,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if playlist is None or user is None:
            return None

        if view_playlist:
            data = PlaylistData(
                title=playlist.title,
                description=playlist.description if playlist.description is not None else " ",
                lang_code=user.chosen_language_code,
            )

            from tase.telegram.bots.ui.inline_buttons.common import get_playlist_markup_keyboard

            return InlineQueryResultArticle(
                title=playlist.title,
                description=f"{playlist.description if playlist.description is not None else ' '}",
                id=f"{cls.get_type_value()}|{telegram_inline_query.id}|{playlist.id}|{ChatType.parse_from_pyrogram(telegram_inline_query.chat_type).value}",
                thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                input_message_content=InputTextMessageContent(
                    message_text=BaseTemplate.registry.playlist_template.render(data),
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=get_playlist_markup_keyboard(
                    playlist,
                    user.chosen_language_code,
                ),
            )
        else:
            return InlineQueryResultArticle(
                title=playlist.title,
                description=f"{playlist.description if playlist.description is not None else ' '}",
                id=f"{cls.get_type_value()}|{telegram_inline_query.id}|{playlist.id}|{ChatType.parse_from_pyrogram(telegram_inline_query.chat_type).value}",
                thumb_url="https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg",
                input_message_content=InputTextMessageContent(
                    message_text=emoji._clock_emoji,
                    parse_mode=ParseMode.HTML,
                ),
            )
