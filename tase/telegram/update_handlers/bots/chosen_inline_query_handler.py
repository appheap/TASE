from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import async_exception_handler
from tase.my_logger import logger
from tase.telegram.bots.ui.base import InlineButton, InlineButtonData, InlineItemInfo
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

    @async_exception_handler()
    async def on_chosen_inline_query(
        self,
        client: pyrogram.Client,
        chosen_inline_result: pyrogram.types.ChosenInlineResult,
    ):
        from_user = await self.db.graph.get_interacted_user(chosen_inline_result.from_user)

        inline_item_info = InlineItemInfo.get_info(chosen_inline_result.result_id)
        if not inline_item_info:
            logger.error(f"Inline chosen inline result:")
            logger.error(chosen_inline_result)
            return

        inline_button_data = InlineButtonData.parse_from_string(chosen_inline_result.query)
        if inline_button_data:
            source_inline_button = InlineButton.find_button_by_type_value(inline_button_data.get_type_value())

            if not source_inline_button or not source_inline_button.is_inline_item_valid(inline_item_info.type):
                return

            # todo: handle downloads from commands like `#download_history` in non-private chats

            await source_inline_button.on_chosen_inline_query(
                self,
                client,
                from_user,
                chosen_inline_result,
                inline_button_data,
                inline_item_info,
            )

        else:
            if not chosen_inline_result.inline_message_id:
                # IMPORTANT: the item does not have any keyboard markup, so it is not considered as inline message. As a result, the `inline_message_id` is
                # not set.
                return

            # IMPORTANT: Since no audio has been sent to the user, the action is not considered a valid download. It'll be counted after the user clicks on the
            #  `download_audio` source_inline_button of the sent message.

            # update the keyboard markup of the downloaded audio

            # await self.update_audio_keyboard_markup(
            #     client,
            #     from_user,
            #     chosen_inline_result,
            #     hit_download_url,
            #     chat_type,
            # )

            # interaction_vertex = await self.db.graph.create_interaction(
            #     hit_download_url,
            #     from_user,
            #     self.telegram_client.telegram_id,
            #     InteractionType.DOWNLOAD,
            #     chat_type,
            # )
            # if not interaction_vertex:
            #     # could not create the interaction_vertex
            #     logger.error("Could not create the `interaction_vertex` vertex:")
            #     logger.error(chosen_inline_result)
            #
