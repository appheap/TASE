import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.common.preprocessing import find_telegram_usernames
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.errors import NotEnoughRamError
from tase.telegram.tasks import AddChannelTask, ReIndexAudiosTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class ReIndexChannelCommand(BaseCommand):
    """
    Reindex a public channel based on its username.
    """

    command_type: BotCommandType = Field(default=BotCommandType.REINDEX_CHANNEL)
    command_description = "Reindex a public channel by its `username`"
    required_role_level: UserRole = UserRole.ADMIN
    number_of_required_arguments = 1

    async def command_function(
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

        chat = await handler.db.graph.get_chat_by_username(channel_username)
        if chat:
            try:
                status, created = await ReIndexAudiosTask(kwargs={"chat_key": chat.key}).publish(handler.db)
            except NotEnoughRamError:
                await message.reply_text(
                    f"Reindexing audio file from chat `{chat.title}` was cancelled due to high memory usage",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                )
            else:
                if status is None:
                    await message.reply_text("internal error")
                else:
                    if created:
                        if status.is_active():
                            await message.reply_text(f"Started reindexing `{chat.title}` channel")
                    else:
                        if status.is_active():
                            await message.reply_text(f"Task for reindexing `{chat.title}` channel is already being processed")
                        else:
                            await message.reply_text(f"The task for reindexing `{chat.title}` channel is already finished")

        else:
            await message.reply_text(
                "This channel does not exist in the Database!",
                quote=True,
                parse_mode=ParseMode.HTML,
            )
            try:
                status, created = await AddChannelTask(kwargs={"channel_username": channel_username}).publish(handler.db)
            except NotEnoughRamError:
                await message.reply_text(
                    f"Adding chat `{channel_username}` was cancelled due to high memory usage",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                )
            else:
                if status is None:
                    await message.reply_text("internal error")
                else:
                    if created:
                        if status.is_active():
                            await message.reply_text(f"Added channel `{channel_username}` to the Database for reindexing.")
                    else:
                        if status.is_active():
                            await message.reply_text(f"Channel with username `{channel_username}` is already being processed")
                        else:
                            await message.reply_text(f"The task for adding channel with username `{channel_username}` is already finished")
