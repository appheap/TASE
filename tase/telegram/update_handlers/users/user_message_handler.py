from typing import List

import pyrogram
from pyrogram import handlers

from tase.common.utils import async_exception_handler
from tase.telegram.update_handlers.base import BaseHandler, HandlerMetadata


class UserMessageHandler(BaseHandler):
    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.MessageHandler,
                callback=self.user_message_handler,
            )
        ]

    @async_exception_handler()
    async def user_message_handler(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
    ):
        await self.update_audio_doc_coming_in_from_archive_channel(message)
