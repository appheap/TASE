from .base_handler import BaseHandler
from ...my_logger import logger
import pyrogram


class ChatMemberUpdatedHandler(BaseHandler):

    def on_chat_member_updated(
            self,
            client: 'pyrogram.Client',
            chat_member_updated: 'pyrogram.types.ChatMemberUpdated'
    ):
        logger.info(f"on_chat_member_updated: {chat_member_updated}")
