from typing import List

from tase.my_logger import logger
import pyrogram
from pyrogram import handlers

from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler


class UserChatMemberUpdatedHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.ChatMemberUpdatedHandler,
                callback=self.chat_member_update_handler,
                group=3
            )
        ]

    @exception_handler
    # todo: not working, why?
    def chat_member_update_handler(
            self,
            client: 'pyrogram.Client',
            chat_member_updated: 'pyrogram.types.ChatMemberUpdated'
    ):
        logger.debug(f"chat_member_update_handler: {chat_member_updated}")
