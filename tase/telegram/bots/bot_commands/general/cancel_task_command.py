import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.update_handlers.base import BaseHandler


class CancelTaskCommand(BaseCommand):
    """
    Cancel the current task for the user
    """

    command_type: BotCommandType = Field(default=BotCommandType.CANCEL)
    command_description = "Cancel the current task"
    required_role_level: UserRole = UserRole.SEARCHER

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        latest_task = handler.db.document.get_latest_bot_task(
            from_user.user_id,
            handler.telegram_client.telegram_id,
        )
        if latest_task is None:
            # user has no task running
            message.reply_text(
                "No task is running!",
                quote=True,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        else:
            canceled = handler.db.document.cancel_recent_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                latest_task.type,
            )
            if canceled:
                message.reply_text(
                    "Task was successfully canceled!",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text(
                    "Could not cancel the due to internal error, please try again.",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
