from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import async_exception_handler
from tase.my_logger import logger
from tase.telegram.bots.ui.base import InlineButton, InlineButtonData
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

        data = InlineButtonData.parse_from_string(callback_query.data)
        if not data:
            await callback_query.answer("", show_alert=False)
            return

        button = InlineButton.find_button_by_type_value(data.get_type_value())
        if not button:
            await callback_query.answer("", show_alert=False)
            return

        await button.on_callback_query(
            self,
            db_user,
            client,
            callback_query,
            data,
        )
