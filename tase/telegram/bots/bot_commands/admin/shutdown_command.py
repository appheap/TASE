import pyrogram
from pydantic import Field

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.task_distribution import ShutdownTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class ShutdownCommand(BaseCommand):
    """
    Shutdown all telegram consumers and pause the scheduler. It is mainly used for maintenance purposes, like having
    a graceful shutdown for upgrading the codebase, etc... .
    """

    command_type: BotCommandType = Field(default=BotCommandType.SHUTDOWN_SYSTEM)
    command_description = "Stop the system to perform an update"
    required_role_level: UserRole = UserRole.OWNER

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        # todo: translate me
        message.reply_text("Starting to shutdown the system...")
        published = ShutdownTask().publish()
        if published:
            message.reply_text("Shutdown command completed successfully.")
        else:
            message.reply_text("Could not shutdown the system.")
