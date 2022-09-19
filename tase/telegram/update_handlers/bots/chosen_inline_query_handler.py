import re
from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import exception_handler
from tase.my_logger import logger
from tase.telegram.bots.ui.inline_buttons.base import InlineButton
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


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
        client: pyrogram.Client,
        chosen_inline_result: pyrogram.types.ChosenInlineResult,
    ):
        logger.debug(f"on_chosen_inline_query: {chosen_inline_result}")

        from_user = self.db.graph.get_or_create_user(chosen_inline_result.from_user)

        reg = re.search(
            "^#(?P<command>[a-zA-Z0-9_]+)(\s(?P<arg1>[a-zA-Z0-9_]+))?",
            chosen_inline_result.query,
        )
        if reg:
            # it's a custom command
            # todo: handle downloads from commands like `#download_history` in non-private chats
            logger.info(chosen_inline_result)

            button = InlineButton.find_button_by_type_value(reg.group("command"))
            if button:
                button.on_chosen_inline_query(
                    self,
                    client,
                    from_user,
                    chosen_inline_result,
                    reg,
                )

        else:
            inline_query_id, hit_download_url = chosen_inline_result.result_id.split(
                "->"
            )

            download_vertex = self.db.graph.create_download(
                hit_download_url,
                from_user,
                self.telegram_client.telegram_id,
            )
            if not download_vertex:
                # could not create the download
                logger.error("Could not create the `download` vertex:")
                logger.error(chosen_inline_result)
