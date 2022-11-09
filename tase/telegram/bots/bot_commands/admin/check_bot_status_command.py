import asyncio

import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType
from ...ui.templates import BaseTemplate, BotStatusData


class CheckBotStatusCommand(BaseCommand):
    """
    Show some basic information about the status of the bot, like how many users have interacted with the bot
    in last 24 hours, etc.
    """

    command_type: BotCommandType = Field(default=BotCommandType.CHECK_BOT_STATUS)
    command_description = "Check the bot status information"
    required_role_level: UserRole = UserRole.ADMIN

    async def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        waiting_message = await message.reply_text(
            emoji._clock_emoji,
            quote=False,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

        new_users_task = asyncio.get_running_loop().run_in_executor(None, handler.db.graph.get_new_joined_users_count)
        total_users_task = asyncio.get_running_loop().run_in_executor(None, handler.db.graph.get_total_users_count)
        new_audios_task = asyncio.get_running_loop().run_in_executor(None, handler.db.graph.get_new_indexed_audio_files_count)
        total_audios_task = asyncio.get_running_loop().run_in_executor(None, handler.db.graph.get_total_indexed_audio_files_count)
        new_queries_task = asyncio.get_running_loop().run_in_executor(None, handler.db.graph.get_new_queries_count)
        total_queries_task = asyncio.get_running_loop().run_in_executor(None, handler.db.graph.get_total_queries_count)

        new_users, total_users, new_audios, total_audios, new_queries, total_queries = await asyncio.gather(
            *[
                new_users_task,
                total_users_task,
                new_audios_task,
                total_audios_task,
                new_queries_task,
                total_queries_task,
            ]
        )

        data = BotStatusData(
            new_users=f"{new_users:,}",
            total_users=f"{total_users:,}",
            new_audios=f"{new_audios:,}",
            total_audios=f"{total_audios:,}",
            new_queries=f"{new_queries:,}",
            total_queries=f"{total_queries:,}",
        )
        delete_task = asyncio.get_running_loop().create_task(waiting_message.delete())
        await message.reply_text(
            BaseTemplate.registry.bot_status_template.render(data),
            quote=True,
            parse_mode=ParseMode.HTML,
        )
        try:
            await delete_task
        except Exception as e:
            logger.exception(e)
