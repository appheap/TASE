import pyrogram
from pydantic import Field

import tase
from tase import tase_globals
from tase.db.graph_models.vertices import UserRole
from tase.telegram.client import worker_commands
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class ShutdownCommand(BaseCommand):
    """
    Shutdown all telegram consumers and pause the scheduler. It is mainly used for maintenance purposes, like having
    a graceful shutdown for upgrading the codebase, etc... .
    """

    command_type: BotCommandType = Field(default=BotCommandType.SHUTDOWN_SYSTEM)
    required_role_level: UserRole = UserRole.ADMIN

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.update_handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:
        # todo: translate me

        message.reply_text("Starting to shutdown the system...")
        tase_globals.broadcast_worker_command_task(worker_commands.ShutdownCommand())
        message.reply_text("Shutdown command completed successfully.")
