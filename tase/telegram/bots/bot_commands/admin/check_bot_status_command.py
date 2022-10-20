import pyrogram
from pydantic import Field

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


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
        pass
