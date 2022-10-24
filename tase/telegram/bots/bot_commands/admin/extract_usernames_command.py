import pyrogram
from pydantic import Field

from tase.common.preprocessing import find_telegram_usernames
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.telegram.tasks import ExtractUsernamesTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class ExtractUsernamesCommand(BaseCommand):
    """
    Extract usernames from a public channel.
    """

    command_type: BotCommandType = Field(default=BotCommandType.EXTRACT_USERNAMES)
    command_description = "Extract usernames from a public channel"
    required_role_level: UserRole = UserRole.OWNER
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

        username_list = find_telegram_usernames(channel_username, return_start_index=False)
        if len(username_list):
            channel_username = username_list[0]

        db_chat = handler.db.graph.get_chat_by_username(channel_username)
        if not db_chat:
            # todo: translate me
            message.reply_text(f"This channel `{channel_username}` does not exist in the Database!")
            kwargs = {"channel_username": channel_username}
        else:
            kwargs = {"chat_key": db_chat.key}

        status, created = ExtractUsernamesTask(kwargs=kwargs).publish(handler.db)
        if status is None:
            message.reply_text("internal error")
        else:
            if created:
                if status.is_active():
                    message.reply_text(f"Added channel `{channel_username}` to the Database for username extraction.")
            else:
                if status.is_active():
                    message.reply_text(f"Channel with username `{channel_username}` is already being processed")
                else:
                    message.reply_text(f"The task for extracting usernames from channel with username `{channel_username}` is already finished")
