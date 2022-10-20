from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import exception_handler
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class UserMessageHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.user_message_handler,
            )
        ]

    @exception_handler
    def user_message_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        direction = "=>" if message.outgoing else "<="
        logger.debug(f"user_message_handler: {direction} {message.chat.title or message.chat.first_name}")
