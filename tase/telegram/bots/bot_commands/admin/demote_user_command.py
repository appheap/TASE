import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    PeerIdInvalid,
)
from pyrogram.types import BotCommandScopeChat

from tase.common.utils import find_telegram_usernames
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from ..base_command import BaseCommand
from ..bot_command_type import BotCommandType


class DemoteUserCommand(BaseCommand):
    """
    Demote a user's role to `searcher`
    """

    command_type: BotCommandType = Field(default=BotCommandType.DEMOTE_USER)
    command_description = "Demote a user's role to searcher"
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

        username_list = find_telegram_usernames(username)
        if len(username_list):
            username = username_list[0][0]

        user = handler.db.graph.get_user_by_username(username)

        if user:
            if user.user_id == from_user.user_id:
                message.reply_text(
                    "You cannot demote yourself!",
                    quote=True,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
            else:
                if user.role == UserRole.SEARCHER:
                    message.reply_text(
                        "The user's role is already `searcher`",
                        quote=True,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                    )

                elif user.role == UserRole.ADMIN:
                    updated = user.update_role(UserRole.SEARCHER)
                    if updated:
                        message.reply_text(
                            "Successfully demoted the user",
                            quote=True,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                        )
                        try:
                            client.delete_bot_commands(
                                BotCommandScopeChat(user.user_id)
                            )
                        except PeerIdInvalid as e:
                            # todo: The peer id being used is invalid or not known yet. Make sure you meet the peer
                            #  before interacting with it
                            pass
                        except Exception as e:
                            logger.exception(e)
                    else:
                        message.reply_text(
                            "The user could not be demoted, please try again",
                            quote=True,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                        )
                elif user.role == UserRole.OWNER:
                    message.reply_text(
                        "User's role is `owner` and cannot be demoted",
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
