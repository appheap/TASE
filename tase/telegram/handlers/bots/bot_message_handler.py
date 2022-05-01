from typing import List

import pyrogram

from tase.my_logger import logger
from pyrogram import handlers
from pyrogram import filters

from tase.telegram.handlers import BaseHandler, HandlerMetadata


class BotMessageHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        handlers_list = [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.start_bot_handler,
                filters=filters.command(['start']),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.base_commands_handler,
                filters=filters.command(['lang', 'help', 'home']),
                group=0,
            ),
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.bot_message_handler,
                group=0,
            ),
        ]
        return handlers_list

    def start_bot_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"start_bot_handler: {message.command}")

    def base_commands_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"base_commands_handler: {message.command}")

    def bot_message_handler(self, client: 'pyrogram.Client', message: 'pyrogram.types.Message'):
        logger.info(f"bot_message_handler: {message}")
