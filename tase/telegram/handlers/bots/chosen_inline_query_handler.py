from typing import List

import pyrogram
from pyrogram import handlers

from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler

import re


class ChosenInlineQueryHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.ChosenInlineResultHandler,
                callback=self.on_chosen_inline_query,
                group=0,
            )
        ]

    @exception_handler
    def on_chosen_inline_query(
            self,
            client: 'pyrogram.Client',
            chosen_inline_result: 'pyrogram.types.ChosenInlineResult'
    ):
        logger.debug(f"on_chosen_inline_query: {chosen_inline_result}")

        if re.search("^#[a-zA-Z0-9_]+", chosen_inline_result.query):
            # it's a custom command
            logger.info(chosen_inline_result)
            pass
        else:
            inline_query_id, audio_key = chosen_inline_result.result_id.split("->")

            db_download = self.db.get_or_create_download_from_chosen_inline_query(
                chosen_inline_result,
                self.telegram_client.telegram_id
            )
