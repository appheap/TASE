import textwrap
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
from .item_info import PlaylistItemInfo


class PlaylistItem(BaseInlineItem):
    __type__ = InlineItemType.PLAYLIST

    __fav_url__ = "https://telegra.ph/file/aa20ca49bd60cab907d3b.png"
    __private_url__ = "https://telegra.ph/file/188fb4171d01e12445dc8.jpg"
    __public_url__ = "https://telegra.ph/file/ac2d210b9b0e5741470a1.jpg"

    @classmethod
    def get_playlist_thumbnail_url(cls, playlist: graph_models.vertices.Playlist) -> str:
        if playlist.is_favorite:
            return cls.__fav_url__

        if playlist.is_public:
            return cls.__public_url__
        else:
            return cls.__private_url__

    @classmethod
    def _get_description(
        cls,
        playlist: elasticsearch_models.Playlist,
        user: graph_models.vertices.User,
    ) -> str:

        description = (
            f"‎{textwrap.shorten(playlist.description if playlist.description is not None else ' ', 25, placeholder='...')}‎"
            "\n"
            f"{emoji._bell} {playlist.subscribers:<9}\t"
            f"{emoji._inbox_tray} {playlist.playlist_downloads:<9}\t"
            f"{emoji._headphone} {playlist.audio_downloads:<9}\t"
            f"{emoji._link} {playlist.shares:<9}"
        )

        return description

    @classmethod
    def get_item(
        cls,
        playlist: graph_models.vertices.Playlist,
        user: graph_models.vertices.User,
        telegram_inline_query: pyrogram.types.InlineQuery,
        view_playlist: Optional[bool] = True,
        hit_download_url: Optional[str] = None,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if playlist is None or user is None:
            return None

        from tase.telegram.bots.ui.inline_items.item_info import PlaylistItemInfo

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

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
                id=PlaylistItemInfo.parse_id(
                    telegram_inline_query,
                    playlist.key,
                    chat_type,
                    hit_download_url,
                ),
                thumb_url=cls.get_playlist_thumbnail_url(playlist),
                input_message_content=InputTextMessageContent(
                    message_text=BaseTemplate.registry.playlist_template.render(data),
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=get_playlist_markup_keyboard(
                    playlist,
                    user,
                    chat_type,
                ),
            )
        else:
            return InlineQueryResultArticle(
                title=playlist.title,
                description=f"{playlist.description if playlist.description is not None else ' '}",
                id=PlaylistItemInfo.parse_id(
                    telegram_inline_query,
                    playlist.key,
                    chat_type,
                    hit_download_url,
                ),
                thumb_url=cls.get_playlist_thumbnail_url(playlist),
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
        hit_download_url: str,
        view_playlist: Optional[bool] = True,
    ) -> Optional[pyrogram.types.InlineQueryResult]:
        if playlist is None or user is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)

        if view_playlist:
            data = PlaylistData(
                title=playlist.title,
                description=playlist.description if playlist.description is not None else " ",
                lang_code=user.chosen_language_code,
            )

            from tase.telegram.bots.ui.inline_buttons.common import get_playlist_markup_keyboard

            return InlineQueryResultArticle(
                title=playlist.title,
                description=cls._get_description(playlist, user),
                id=PlaylistItemInfo.parse_id(
                    telegram_inline_query,
                    playlist.id,
                    chat_type,
                    hit_download_url=hit_download_url,
                ),
                thumb_url=cls.__public_url__,
                input_message_content=InputTextMessageContent(
                    message_text=BaseTemplate.registry.playlist_template.render(data),
                    parse_mode=ParseMode.HTML,
                ),
                reply_markup=get_playlist_markup_keyboard(
                    playlist,
                    user,
                    chat_type,
                ),
            )
        else:
            return InlineQueryResultArticle(
                title=playlist.title,
                description=cls._get_description(playlist, user),
                id=PlaylistItemInfo.parse_id(
                    telegram_inline_query,
                    playlist.id,
                    chat_type,
                    hit_download_url=hit_download_url,
                ),
                thumb_url=cls.__public_url__,
                input_message_content=InputTextMessageContent(
                    message_text=emoji._clock_emoji,
                    parse_mode=ParseMode.HTML,
                ),
            )
