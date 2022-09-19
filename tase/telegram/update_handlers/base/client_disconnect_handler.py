from typing import List

import arrow
import pyrogram
from pyrogram import handlers

from tase.common.utils import exception_handler
from tase.my_logger import logger
from .base_handler import BaseHandler
from .handler_metadata import HandlerMetadata


class ClientDisconnectHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.DisconnectHandler,
                callback=self.on_disconnect,
                has_filter=False,
            )
        ]

    @exception_handler
    def on_disconnect(
        self,
        client: pyrogram.Client,
    ):
        logger.info(f"client {client.name} disconnected @ {arrow.utcnow()}")
