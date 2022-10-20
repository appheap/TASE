import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
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

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        data = BotStatusData(
            new_users=f"{handler.db.graph.get_new_joined_users_count():,}",
            total_users=f"{handler.db.graph.get_total_users_count():,}",
            new_audios=f"{handler.db.graph.get_new_indexed_audio_files_count():,}",
            total_audios=f"{handler.db.graph.get_total_indexed_audio_files_count():,}",
            new_queries=f"{handler.db.graph.get_new_queries_count():,}",
            total_queries=f"{handler.db.graph.get_total_queries_count():,}",
        )
        message.reply_text(
            BaseTemplate.registry.bot_status_template.render(data),
            quote=True,
            parse_mode=ParseMode.HTML,
        )
