from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import async_exception_handler
from tase.my_logger import logger
from tase.telegram.bots.ui.inline_buttons.base import InlineButton
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class CallbackQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.CallbackQueryHandler,
                callback=self.on_callback_query,
            )
        ]

    @async_exception_handler()
    async def on_callback_query(
        self,
        client: pyrogram.Client,
        callback_query: pyrogram.types.CallbackQuery,
    ):
        logger.debug(f"on_callback_query: {callback_query}")
        db_user = await self.db.graph.get_interacted_user(callback_query.from_user)

        button_type_value, data, chat_type_value = callback_query.data.split("->")
        button = InlineButton.find_button_by_type_value(button_type_value)

        if button:
            await button.on_callback_query(
                self,
                db_user,
                client,
                callback_query,
            )
        else:
            await callback_query.answer("", show_alert=False)
