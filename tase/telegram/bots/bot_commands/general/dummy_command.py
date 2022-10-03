import pyrogram
from pydantic import Field

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.tasks import DummyTask
from tase.telegram.update_handlers.base import BaseHandler


class DummyCommand(BaseCommand):
    """
    Publishes a dummy task to be executed. It is meant only for test purposes.
    """

    command_type: BotCommandType = Field(default=BotCommandType.DUMMY)
    command_description = "This is command for testing purposes"
    required_role_level: UserRole = UserRole.OWNER

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        DummyTask().publish()
