from typing import List

import pyrogram
from pyrogram import handlers

from tase.my_logger import logger
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
        logger.debug(f"on_chosen_inline_query: {chosen_inline_result}")

        db_download = self.db.get_or_create_download(
            chosen_inline_result,
            self.telegram_client.telegram_id
        )
