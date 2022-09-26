import pyrogram
from pydantic import Field

from tase import tase_globals
from tase.common.utils import find_telegram_usernames
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.telegram.client.tasks import IndexAudiosTask, AddChannelTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class IndexChannelCommand(BaseCommand):
    """
    Index a public channel based on its username.
    """

    command_type: BotCommandType = Field(default=BotCommandType.INDEX_CHANNEL)
    command_description = "Index a public channel by its `username`"
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
        if db_chat:
            tase_globals.publish_client_task(
                IndexAudiosTask(kwargs={"chat": db_chat}),
            )
            # todo: translate me
            message.reply_text(f"Started indexing `{db_chat.title}` channel")

        else:
            message.reply_text("This channel does not exist in the Database!")
            tase_globals.publish_client_task(
                AddChannelTask(kwargs={"channel_username": channel_username}),
            )
            # todo: translate me
            message.reply_text("Added channel to the Database for indexing.")