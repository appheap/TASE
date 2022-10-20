from __future__ import annotations

import re
from typing import List

import pyrogram
from pyrogram import filters, handlers

from tase.common.preprocessing import telegram_url_regex, url_regex
from tase.common.utils import exception_handler, get_now_timestamp
from tase.errors import NullTelegramInlineQuery
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult, InlineSearch
from tase.telegram.bots.ui.inline_buttons.base import InlineButton
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class InlineQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.custom_commands_handler,
                filters=filters.regex(r"^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?"),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.on_inline_query,
                filters=~filters.bot & ~filters.regex(telegram_url_regex) & ~filters.regex(url_regex) & ~filters.regex("^(.*/+.*)+$"),
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

        from_user = self.db.graph.get_interacted_user(inline_query.from_user)

        result = CustomInlineQueryResult(inline_query)
        InlineSearch.on_inline_query(
            self,
            result,
            from_user,
            client,
            inline_query,
            query_date,
        )
        try:
            result.answer_query(inline_query)
        except NullTelegramInlineQuery:
            pass
        except Exception as e:
            logger.exception(e)

    @exception_handler
    def custom_commands_handler(
        self,
        client: pyrogram.Client,
        inline_query: pyrogram.types.InlineQuery,
    ):
        logger.debug(f"custom_commands_handler: {inline_query}")
        query_date = get_now_timestamp()

        user = self.db.graph.get_interacted_user(inline_query.from_user)

        reg = re.search(
            r"^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?",
            inline_query.query,
        )
        button = InlineButton.find_button_by_type_value(reg.group("command"))
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
            try:
                result.answer_query(inline_query)
            except NullTelegramInlineQuery:
                pass
            except Exception as e:
                logger.exception(e)
        else:
            pass
