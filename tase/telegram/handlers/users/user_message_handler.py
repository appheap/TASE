from typing import List

import pyrogram
from pyrogram import handlers
from tase.my_logger import logger
from tase.telegram.globals import client_task
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler
from tase.telegram.tasks import IndexAudiosTask


class UserMessageHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.user_message_handler,
            )
        ]

    @exception_handler
    def user_message_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        direction = '=>' if message.outgoing else '<='
        logger.debug(f"user_message_handler: {direction} {message.chat.title or message.chat.first_name}")

        # todo: temp solution
        from .temp import func
        func(client, self.telegram_client, message, logger, self.task_queues)
