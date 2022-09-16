from __future__ import annotations

import re
from typing import List

import pyrogram
from pyrogram import filters, handlers

from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult, InlineSearch
from tase.telegram.bots.ui.inline_buttons import InlineButton
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata
from tase.utils import exception_handler, get_now_timestamp

known_mime_types = (
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/mpeg3",
    "audio/flac",
    "audio/ogg",
    "audio/MP3",
    "audio/x-vorbis+ogg",
    "audio/x-opus+ogg",
)

forbidden_mime_types = (
    "audio/ogg",
    "audio/x-vorbis+ogg",
    "audio/x-opus+ogg",
)


class InlineQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.custom_commands_handler,
                filters=filters.regex(
                    r"^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?"
                ),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.on_inline_query,
                group=0,
            ),
        ]

    @exception_handler
    def on_inline_query(
        self,
        client: pyrogram.Client,
        inline_query: pyrogram.types.InlineQuery,
    ):
        logger.debug(f"on_inline_query: {inline_query}")
        query_date = get_now_timestamp()

        from_user = self.db.graph.get_or_create_user(inline_query.from_user)

        result = CustomInlineQueryResult(inline_query)
        InlineSearch.on_inline_query(
            self,
            result,
            from_user,
            client,
            inline_query,
            query_date,
        )
        result.answer_query(inline_query)

    @exception_handler
    def custom_commands_handler(
        self,
        client: pyrogram.Client,
        inline_query: pyrogram.types.InlineQuery,
    ):
        logger.debug(f"custom_commands_handler: {inline_query}")
        query_date = get_now_timestamp()

        user = self.db.graph.get_or_create_user(inline_query.from_user)

        reg = re.search(
            r"^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?",
            inline_query.query,
        )
        button = InlineButton.get_button(reg.group("command"))
        if button:
            result = CustomInlineQueryResult(inline_query)
            button.on_inline_query(
                self,
                result,
                user,
                client,
                inline_query,
                query_date,
                reg,
            )
            result.answer_query(inline_query)
        else:
            pass
