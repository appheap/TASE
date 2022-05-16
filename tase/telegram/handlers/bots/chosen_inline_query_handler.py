import re
from typing import List

import pyrogram
from pyrogram import handlers

from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata, exception_handler
from tase.telegram.inline_buton_globals import buttons


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

        # todo: fix this
        db_from_user = self.db.get_user_by_user_id(chosen_inline_result.from_user.id)
        if not db_from_user:
            # update the user
            db_from_user = self.db.update_or_create_user(chosen_inline_result.from_user)

        if re.search("^#[a-zA-Z0-9_]+", chosen_inline_result.query):
            # it's a custom command
            # todo: handle downloads from commands like `#download_history` in non-private chats
            logger.info(chosen_inline_result)

            command = chosen_inline_result.query.split('#')[1]

            try:
                command = command.split(" ")[0]
            except:
                pass
            if command in buttons.keys():
                button = buttons[command]
                button.on_chosen_inline_query(
                    client,
                    chosen_inline_result,
                    self,
                    self.db,
                    self.telegram_client,
                    db_from_user,
                )

        else:
            inline_query_id, audio_key = chosen_inline_result.result_id.split("->")

            db_download = self.db.get_or_create_download_from_chosen_inline_query(
                chosen_inline_result,
                self.telegram_client.telegram_id
            )
