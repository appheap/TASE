import pyrogram
from pydantic import Field

from tase import globals
from tase.db.graph_models.vertices import UserRole
from tase.telegram.client.tasks import AddChannelTask
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class AddChannelCommand(BaseCommand):
    """
    Adds a new channel to the Database to be indexed.
    """

    command_type: BotCommandType = Field(default=BotCommandType.ADD_CHANNEL)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:

        # todo: this is need to be check for all admin/owner commands.
        # check if the user has permission to execute admin/owner commands
        if db_from_user.role not in (UserRole.ADMIN, UserRole.OWNER):
            # todo: log users who query these commands without having permission
            return

        if len(message.command) == 2:
            channel_username = message.command[1]

            # todo: check if the username is in valid format

            db_chat = handler.db.get_chat_by_username(channel_username)
            if db_chat:
                # todo: translate me
                message.reply_text("This channel already exists in the Database!")
            else:
                globals.publish_client_task(
                    AddChannelTask(kwargs={"channel_username": channel_username}),
                    globals.tase_telegram_queue,
                )
                # todo: translate me
                message.reply_text("Added Channel to the Database for indexing.")
        else:
            # fixme: `index` command haven't been provided with `channel_username` argument
            pass
