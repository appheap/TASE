from typing import List

import pyrogram

from tase.my_logger import logger

from pyrogram import handlers

from tase.telegram.handlers import HandlerMetadata, BaseHandler


class CallbackQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.CallbackQueryHandler,
                callback=self.on_callback_query,
            )
        ]

    def on_callback_query(self, client: 'pyrogram.Client', callback_query: 'pyrogram.types.CallbackQuery'):
        logger.info(f"on_callback_query: {callback_query}")
        # callback_query.edit_message_caption(str(arrow.utcnow()),reply_markup=callback_query.message.reply_markup)
        # callback_query.answer(str(arrow.utcnow()))
        callback_query.answer('simple answer')
