import pyrogram

from .base_handler import BaseHandler
from ...my_logger import logger


class CallbackQueryHandler(BaseHandler):

    def on_callback_query(self, client: 'pyrogram.Client', callback_query: 'pyrogram.types.CallbackQuery'):
        logger.info(f"on_callback_query: {callback_query}")
        # callback_query.edit_message_caption(str(arrow.utcnow()),reply_markup=callback_query.message.reply_markup)
        # callback_query.answer(str(arrow.utcnow()))
