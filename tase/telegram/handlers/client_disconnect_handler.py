import arrow
import pyrogram

from .base_handler import BaseHandler
from ...my_logger import logger


class ClientDisconnectHandler(BaseHandler):
    def on_disconnect(self, client: 'pyrogram.Client'):
        logger.info(f"client {client.name} disconnected @ {arrow.utcnow()}")
