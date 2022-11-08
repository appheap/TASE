import asyncio

import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.errors import NotEnoughRamError
from tase.telegram.tasks import CheckUsernameTask
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class CheckUsernamesCommand(BaseCommand):
    """
    Check all unchecked usernames in the database.
    """

    command_type: BotCommandType = Field(default=BotCommandType.CHECK_USERNAMES)
    command_description = "Check unchecked usernames in the database"
    required_role_level: UserRole = UserRole.OWNER
    number_of_required_arguments = 0

    async def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        usernames = handler.db.graph.get_unchecked_usernames()

        for idx, username in enumerate(usernames):
            # todo: blocking or non-blocking? which one is better suited for this case?
            try:
                await CheckUsernameTask(
                    kwargs={
                        "username_key": username.key,
                    }
                ).publish(handler.db)
            except NotEnoughRamError:
                await message.reply_text(
                    f"Checking usernames was cancelled due to high memory usage",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                )
                break
            else:
                if idx > 0 and idx % 10 == 0:
                    # fixme: sleep to avoid publishing many tasks while the others haven't been processed yet
                    await asyncio.sleep(10 * 15)
