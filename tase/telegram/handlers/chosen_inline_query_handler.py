import pyrogram

from .base_handler import BaseHandler
from ...my_logger import logger


class ChosenInlineQueryHandler(BaseHandler):
    def on_chosen_inline_query(
            self,
            client: 'pyrogram.Client',
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult'
    ):
        logger.info(f"on_chosen_inline_query: {chosen_inline_result}")
