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
        if message.chat.id == 61709467:
            if not message.media:
                try:
                    logger.info(self.task_queues)
                    q = self.task_queues[self.telegram_client.name]
                    chat = client.get_chat(chat_id=message.text)
                    client_task(
                        IndexAudiosTask(kwargs={'chat_id': chat.id}),
                        target_queue=q
                    )
                except Exception as e:
                    logger.exception(e)
