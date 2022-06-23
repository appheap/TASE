from typing import List

import pyrogram
from pyrogram import handlers

from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler
from tase.telegram.inline_buttons import InlineButton


class CallbackQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.CallbackQueryHandler,
                callback=self.on_callback_query,
            )
        ]

    @exception_handler
    def on_callback_query(
        self, client: "pyrogram.Client", callback_query: "pyrogram.types.CallbackQuery"
    ):
        logger.debug(f"on_callback_query: {callback_query}")
        # callback_query.edit_message_caption(str(arrow.utcnow()),reply_markup=callback_query.message.reply_markup)
        db_user = self.db.get_user_by_user_id(callback_query.from_user.id)

        controller, data = callback_query.data.split("->")
        button = InlineButton.get_button(controller)

        if button:
            button.on_callback_query(
                client,
                callback_query,
                self,
                self.db,
                self.telegram_client,
                db_user,
            )
        else:
            callback_query.answer("", show_alert=False)
