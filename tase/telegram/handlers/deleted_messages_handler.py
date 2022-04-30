from typing import List

import arrow
import pyrogram

from .base_handler import BaseHandler
from ...my_logger import logger


class DeletedMessagesHandler(BaseHandler):

    def deleted_messages_handler(self, client: 'pyrogram.Client', messages: List['pyrogram.types.Message']):
        logger.info(f"deleted_messages_handler: {messages}")
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
