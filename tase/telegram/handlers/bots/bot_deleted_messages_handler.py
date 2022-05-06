from __future__ import annotations

from typing import List

import arrow
import pyrogram
from pyrogram import handlers

from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler


class BotDeletedMessagesHandler(BaseHandler):

    def init_handlers(self) -> List['HandlerMetadata']:
        return [
            HandlerMetadata(
                cls=handlers.DeletedMessagesHandler,
                callback=self.deleted_messages_handler,
                has_filter=False,
                group=2
            )
        ]

    @exception_handler
    # todo: not working, why?
    def deleted_messages_handler(self, client: 'pyrogram.Client', messages: List['pyrogram.types.Message']):
        logger.debug(f"bot_deleted_messages_handler: {messages}")
        estimate_date_of_deletion = arrow.utcnow().timestamp()
        for message in messages:
            if message.chat is None:
                # deleted message is from `saved messages`
                message_id = message.id
            else:
                # deleted message if from other chats
                message_id = message.id
                chat_id: int = message.chat.id
                chat_type: str = message.chat.type.name
