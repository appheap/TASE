from typing import List

import pyrogram

from tase.my_logger import logger

from pyrogram import handlers

from tase.telegram.handlers import HandlerMetadata, BaseHandler, exception_handler


class CallbackQueryHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.CallbackQueryHandler,
                callback=self.on_callback_query,
            )
        ]

    @exception_handler
    def on_callback_query(self, client: 'pyrogram.Client', callback_query: 'pyrogram.types.CallbackQuery'):
        logger.debug(f"on_callback_query: {callback_query}")
        # callback_query.edit_message_caption(str(arrow.utcnow()),reply_markup=callback_query.message.reply_markup)
        # callback_query.answer(str(arrow.utcnow()))
        callback_query.answer('simple answer')

        db_user = self.db.get_user_by_user_id(callback_query.from_user.id)
        controller, data = callback_query.data.split('->')
        if controller == 'choose_language':
            callback_query.message.delete()
            self.db.update_user_chosen_language(db_user, data)
        else:
            pass
