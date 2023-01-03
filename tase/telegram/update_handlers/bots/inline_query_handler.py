from __future__ import annotations

from typing import List

import pyrogram
from pyrogram import filters, handlers

from tase.common.preprocessing import telegram_url_regex, url_regex
from tase.common.utils import get_now_timestamp, async_timed, async_exception_handler
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult, InlineSearch
from tase.telegram.bots.ui.base import InlineButton, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class InlineQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.custom_commands_handler,
                filters=filters.regex(r"^$(?P<command>[a-zA-Z0-9_]+)"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.on_inline_query,
                filters=~filters.bot & ~filters.regex(telegram_url_regex) & ~filters.regex(url_regex) & ~filters.regex("^(.*/+.*)+$"),
                group=0,
            ),
        ]

    @async_exception_handler()
    @async_timed()
    async def on_inline_query(
        self,
        client: pyrogram.Client,
        inline_query: pyrogram.types.InlineQuery,
    ):
        from_user = await self.db.graph.get_interacted_user(inline_query.from_user)
        query_date = get_now_timestamp()

        await InlineSearch.on_inline_query(
            self,
            CustomInlineQueryResult(inline_query),
            from_user,
            client,
            inline_query,
            query_date,
        )

    @async_exception_handler()
    @async_timed()
    async def custom_commands_handler(
        self,
        client: pyrogram.Client,
        inline_query: pyrogram.types.InlineQuery,
    ):
        user = await self.db.graph.get_interacted_user(inline_query.from_user)
        query_date = get_now_timestamp()

        data = InlineButtonData.parse_from_string(inline_query.query)
        if not data:
            logger.error(f"invalid custom inline query: {inline_query}")
            return

        button = InlineButton.find_button_by_type_value(data.get_type_value())
        if not button:
            logger.error(f"invalid custom inline query: {inline_query}")
            return

        await button.on_inline_query(
            self,
            CustomInlineQueryResult(inline_query),
            user,
            client,
            inline_query,
            query_date,
            data,
        )
