import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    FloodWait,
    UsernameNotOccupied,
    UsernameInvalid,
    PeerIdInvalid,
)

from tase.common.utils import find_telegram_usernames
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
    command_description = "Promote a user to admin"
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
                    "You cannot promote yourself!",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            else:
                if user.role == UserRole.SEARCHER:
                    updated = user.update_role(UserRole.ADMIN)
                    if updated:
                        message.reply_text(
                            "The user promoted successfully",
                            quote=True,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )
                    else:
                        message.reply_text(
                            "The user could not be promoted, please try again",
                            quote=True,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )
                elif user.role == UserRole.ADMIN:
                    message.reply_text(
                        "The user is already promoted",
                        quote=True,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
                elif user.role == UserRole.OWNER:
                    message.reply_text(
                        "You have the `owner` role already",
                        quote=True,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
        else:
            try:
                tg_chat: pyrogram.types.Chat = handler.telegram_client.get_chat(
                    username
                )
            except (
                KeyError,
                ValueError,
                UsernameNotOccupied,
                UsernameInvalid,
                PeerIdInvalid,
            ) as e:
                # ValueError: In case the chat invite link points to a chat that this telegram client hasn't joined yet.
                # KeyError or UsernameNotOccupied: The username is not occupied by anyone, so update the username
                # UsernameInvalid: The username is invalid

                message.reply_text(
                    f"Username `{username}` is not valid",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

            except FloodWait as e:
                # fixme: find a solution for this
                pass
            except Exception as e:
                message.reply_text(
                    "Internal error, please try again",
                    quote=True,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                logger.exception(e)
            else:
                if tg_chat:
                    user = handler.db.graph.get_or_create_user(tg_chat)
                    if user:
                        updated = user.update_role(UserRole.ADMIN)
                        if updated:
                            message.reply_text(
                                "The user promoted successfully",
                                quote=True,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=True,
                            )

                            # todo: cache the user peer for all the bots
                        else:
                            message.reply_text(
                                "The user could not be promoted, please try again",
                                quote=True,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=True,
                            )
                    else:
                        message.reply_text(
                            "Internal error, please try again",
                            quote=True,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )
                else:
                    message.reply_text(
                        "Internal error, please try again",
                        quote=True,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
