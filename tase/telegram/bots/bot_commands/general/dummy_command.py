import pyrogram
from pydantic import Field

import tase
from tase import tase_globals
from tase.db.graph_models.vertices import UserRole
from tase.my_logger import logger
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.client.tasks import DummyTask


class DummyCommand(BaseCommand):
    """
    Publishes a dummy task to be executed. It is meant only for test purposes.
    """

    command_type: BotCommandType = Field(default=BotCommandType.DUMMY)
    required_role_level: UserRole = UserRole.OWNER

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.update_handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:
        logger.info(f"Got dummy command")
        tase_globals.publish_client_task(DummyTask())
