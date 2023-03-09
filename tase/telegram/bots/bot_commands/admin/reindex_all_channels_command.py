import asyncio
import random

import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.errors import NotEnoughRamError
from tase.my_logger import logger
from tase.telegram.tasks import ReindexAudiosTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class ReindexAllChannelsCommand(BaseCommand):
    """
    Reindex all indexed public channels.
    """

    command_type: BotCommandType = Field(default=BotCommandType.REINDEX_CHANNELS)
    command_description = "Reindex all public channels"
    required_role_level: UserRole = UserRole.OWNER
    number_of_required_arguments = 1

    async def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        confirm_message = message.command[1]

        if confirm_message.strip().lower() != "confirm":
            await message.reply_text(
                "The `confirm` word must be passed with the command!",
                quote=True,
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        await message.reply_text(
            "Started reindexing all public channels...",
            quote=True,
            parse_mode=ParseMode.MARKDOWN,
        )

        # todo: blocking or non-blocking? which one is better suited for this case?
        async for chat in handler.db.graph.get_chats_sorted_by_audio_indexer_score(only_include_indexed_chats=True):
            logger.info(f"published task for reindexing: {chat.username}")
            try:
                await ReindexAudiosTask(
                    kwargs={
                        "chat_key": chat.key,
                    }
                ).publish(handler.db)
            except NotEnoughRamError:
                logger.error(f"Reindexing audio files for chat `{chat.username}` was cancelled due to high memory usage")
                break
            except Exception as e:
                logger.exception(e)
                break
            else:
                await asyncio.sleep(random.randint(3, 10))
