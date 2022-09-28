import re
from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import exception_handler
from tase.db.arangodb.enums import InteractionType, ChatType
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

        from_user = self.db.graph.get_interacted_user(chosen_inline_result.from_user)

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
            (
                inline_query_id,
                hit_download_url,
                chat_type_value,
                _,
            ) = chosen_inline_result.result_id.split("->")

            chat_type = ChatType(int(chat_type_value))

            interaction_vertex = self.db.graph.create_interaction(
                hit_download_url,
                from_user,
                self.telegram_client.telegram_id,
                InteractionType.DOWNLOAD,
                chat_type,
            )
            if not interaction_vertex:
                # could not create the interaction_vertex
                logger.error("Could not create the `interaction_vertex` vertex:")
                logger.error(chosen_inline_result)
