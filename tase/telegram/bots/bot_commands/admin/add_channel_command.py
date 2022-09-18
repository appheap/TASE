import pyrogram
from pydantic import Field

from tase import tase_globals
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.telegram.client.tasks import AddChannelTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class AddChannelCommand(BaseCommand):
    """
    Adds a new channel to the Database to be indexed.
    """

    command_type: BotCommandType = Field(default=BotCommandType.ADD_CHANNEL)
    required_role_level: UserRole = UserRole.ADMIN
    number_of_required_arguments = 1

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        channel_username = message.command[1]

        # todo: check if the username is in valid format

        db_chat = handler.db.graph.get_chat_by_username(channel_username)
        if db_chat:
            # todo: translate me
            message.reply_text("This channel already exists in the Database!")
        else:
            tase_globals.publish_client_task(
                AddChannelTask(kwargs={"channel_username": channel_username}),
            )
            # todo: translate me
            message.reply_text("Added Channel to the Database for indexing.")
