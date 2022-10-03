import pyrogram
from pydantic import Field

from tase.common.utils import find_telegram_usernames
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.task_distribution import task_globals
from tase.telegram.client.tasks import AddChannelTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class AddChannelCommand(BaseCommand):
    """
    Adds a new channel to the Database to be indexed.
    """

    command_type: BotCommandType = Field(default=BotCommandType.ADD_CHANNEL)
    command_description = "Add a public channel `username` to be indexed"
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

        username_list = find_telegram_usernames(channel_username)
        if len(username_list):
            channel_username = username_list[0][0]

        db_chat = handler.db.graph.get_chat_by_username(channel_username)
        if db_chat and db_chat.audio_indexer_metadata:
            # todo: translate me
            message.reply_text(
                f"This channel `{db_chat.title}` already exists in the Database!"
            )
        else:
            task_globals.publish_client_task(
                AddChannelTask(kwargs={"channel_username": channel_username}),
            )
            # todo: translate me
            message.reply_text(
                f"Added channel `{channel_username}` to the Database for indexing."
            )
