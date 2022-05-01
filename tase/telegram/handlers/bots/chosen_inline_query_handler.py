from typing import List

import pyrogram

from tase.my_logger import logger
from pyrogram import handlers

from tase.telegram.handlers import BaseHandler, HandlerMetadata


class ChosenInlineQueryHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.ChosenInlineResultHandler,
                callback=self.on_chosen_inline_query,
            )
        ]

    def on_chosen_inline_query(
            self,
            client: 'pyrogram.Client',
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult'
    ):
        logger.info(f"on_chosen_inline_query: {chosen_inline_result}")
