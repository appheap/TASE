import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    PeerIdInvalid,
)

from tase.common.preprocessing import find_telegram_usernames
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class PromoteUserCommand(BaseCommand):
    """
    Promote a user's role to `admin`
    """

    command_type: BotCommandType = Field(default=BotCommandType.PROMOTE_USER)
    command_description = "Promote a user's role to admin"
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
        username = message.command[1]

        username_list = find_telegram_usernames(username, return_start_index=False)
        if len(username_list):
            username = username_list[0]

        user = handler.db.graph.get_user_by_username(username)

        if user:
            if user.has_interacted_with_bot:
                if user.user_id == from_user.user_id:
                    message.reply_text(
                        "You cannot promote yourself!",
                        quote=True,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    )
                else:
                    if user.role == UserRole.SEARCHER:
                        updated = user.update_role(UserRole.ADMIN)
                        if updated:
                            message.reply_text(
                                "The user promoted successfully",
                                quote=True,
                                parse_mode=ParseMode.MARKDOWN,
                                disable_web_page_preview=True,
                            )
                            telegram_command_dict = handler.db.graph.get_bot_command_for_telegram_user(
                                user,
                                UserRole.ADMIN,
                            )
                            try:
                                client.set_bot_commands(
                                    commands=telegram_command_dict["commands"],
                                    scope=telegram_command_dict["scope"],
                                )
                            except PeerIdInvalid as e:
                                # todo: cache the user peer for all the bots
                                pass
                            except Exception as e:
                                logger.exception(e)
                        else:
                            message.reply_text(
                                "The user could not be promoted, please try again",
                                quote=True,
                                parse_mode=ParseMode.MARKDOWN,
                                disable_web_page_preview=True,
                            )
                    elif user.role == UserRole.ADMIN:
                        message.reply_text(
                            "The user is already promoted",
                            quote=True,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                        )
                    elif user.role == UserRole.OWNER:
                        message.reply_text(
                            "User's role is `owner`",
                            quote=True,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                        )
            else:
                message.reply_text(
                    "This User is in the database but hasn't interacted with the bot yet",
                    quote=True,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
        else:
            message.reply_text(
                "User hasn't interacted with the bot yet",
                quote=True,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
