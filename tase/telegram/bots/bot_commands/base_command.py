from __future__ import annotations

import collections
from typing import List, Optional

import pyrogram
from pydantic import BaseModel, Field
from pyrogram.types import BotCommand

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.graph.vertices.user import UserRole, User
from tase.my_logger import logger
from .bot_command_type import BotCommandType
from ...update_handlers.base import BaseHandler


class BaseCommand(BaseModel):
    """
    This class is used as the base class for all other commands to inherit from.
    Any class who inherits from this class needs to implement
    :meth:`~tase.telegram.bots.bot_commands.BaseCommand.command_function` method.


    Attributes
    ----------
    command_type : BotCommandType
        Type of this command
    command_description: str
        Description of the command (A maximum of 100 characters is allowed)
    required_role_level : UserRole
        Role level required to execute this command
    number_of_required_arguments : int
        Number of arguments necessary to run this command
    """

    command_type: BotCommandType = Field(default=BotCommandType.HELP)
    command_description: str
    required_role_level: UserRole = Field(default=UserRole.SEARCHER)
    number_of_required_arguments: int = Field(default=0)

    _registry = dict()

    @classmethod
    def __init_subclass__(cls) -> None:
        logger.info(f"init subclass of BaseCommand: {cls.__name__}")
        temp = cls()
        BaseCommand._registry[str(temp.command_type.value)] = temp

    @classmethod
    def get_command(
        cls,
        bot_command_type: BotCommandType,
    ) -> Optional[BaseCommand]:
        if bot_command_type is None:
            return None
        return cls._registry.get(str(bot_command_type.value), None)

    @classmethod
    def run_command_from_callback_query(
        cls,
        client: pyrogram.Client,
        callback_query: pyrogram.types.CallbackQuery,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        bot_command_type: BotCommandType,
    ) -> None:
        if client is None or callback_query is None or handler is None or from_user is None or bot_command_type is None:
            return

        command = BaseCommand.get_command(bot_command_type)
        if command:
            cls._authorize_and_execute(
                client,
                command,
                from_user,
                handler,
                callback_query.message,
                True,
            )

    @classmethod
    def run_command(
        cls,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        bot_command_type: Optional[BotCommandType] = None,
    ) -> None:
        if client is None or message is None or handler is None or message.from_user is None:
            return

        logger.error(BotCommandType.get_from_message(message))

        bot_command_type = bot_command_type if bot_command_type is not None else BotCommandType.get_from_message(message)
        if bot_command_type != BotCommandType.INVALID:
            command = BaseCommand.get_command(bot_command_type)
            if message.command is not None and len(message.command) - 1 < command.number_of_required_arguments:
                # todo: translate me
                message.reply_text(
                    "Not enough arguments are provided to run this command",
                    quote=True,
                    disable_web_page_preview=True,
                )
                return

            user: User = handler.db.graph.get_interacted_user(message.from_user)
            if user is None:
                raise Exception(f"Could not get/create user vertex from: {message.from_user}")

            cls._authorize_and_execute(
                client,
                command,
                user,
                handler,
                message,
                False,
            )

    @classmethod
    def _authorize_and_execute(
        cls,
        client: pyrogram.Client,
        command: BaseCommand,
        from_user: User,
        handler: BaseHandler,
        message: pyrogram.types.Message,
        from_callback_query: bool,
    ) -> None:
        """
        Authorize and execute a given command.

        Parameters
        ----------
        client : pyrogram.Client
            Client which received this command
        command : BaseCommand
            Command to be executed
        from_user : graph_models.vertices.User
            User who requested this command
        handler : BaseHandler
            Update handler which originally received the update
        message : pyrogram.types.Message
            Message containing the command
        from_callback_query : bool
            Whether this command came from a direct bot command or was originated from a callback query function.
            Note that when this argument is true, the `message.from_user` is no longer the user, but it's the client
            (most likely a BOT) who sent this message as a reply to an earlier query of the user.

        Returns
        -------
        None:
            This method does not return anything.
        """
        if from_callback_query is None:
            return

            # check if the user has permission to execute this command
        if from_user.role.value >= command.required_role_level.value:
            try:
                command.command_function(client, message, handler, from_user, from_callback_query)
            except NotImplementedError:
                pass
            except Exception as e:
                logger.exception(e)
        else:
            # todo: log users who query these commands without having permission
            message.reply_text(
                _trans(
                    "You don't have the required permission to execute this command!",
                    from_user.chosen_language_code,
                ),
                quote=True,
                disable_web_page_preview=True,
            )

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        raise NotImplementedError

    @classmethod
    def get_command_strings(cls, bot_command_types: List[BotCommandType]) -> List[str]:
        """
        This function converts a list of bot command types to a list of command string to used in pyrogram updated
        handlers

        Parameters
        ----------
        bot_command_types : List[BotCommandType]
            List of bot commands to be converted

        Returns
        -------
        List[str]
            List of command strings if successful otherwise it raises an exception
        """
        if bot_command_types is None or not len(bot_command_types):
            raise ValueError(f"bot_command_types list cannot be empty")

        lst = collections.deque()
        for bot_command_type in bot_command_types:
            if bot_command_type not in (
                BotCommandType.INVALID,
                BotCommandType.UNKNOWN,
                BotCommandType.BASE,
            ):
                command = BaseCommand.get_command(bot_command_type)
                if command:
                    lst.append(str(command.command_type.value))

        return list(lst)

    @classmethod
    def get_all_valid_commands(cls) -> List[str]:
        """
        Get list of all valid command type string.

        Returns
        -------
        List[str]
            List of all command types
        """
        return cls.get_command_strings(list(BotCommandType))

    @classmethod
    def get_commands_for_a_role(
        cls,
        role: UserRole,
    ) -> List[BaseCommand]:
        return sorted(
            filter(
                lambda c: c is not None and c.required_role_level.value <= role.value,
                map(
                    BaseCommand.get_command,
                    filter(
                        lambda c_type: c_type
                        not in (
                            BotCommandType.INVALID,
                            BotCommandType.UNKNOWN,
                            BotCommandType.BASE,
                        ),
                        list(BotCommandType),
                    ),
                ),
            ),
            key=lambda c: str(c.command_type.value),
        )

    @classmethod
    def populate_commands(cls, role: UserRole) -> List[BaseCommand]:
        commands = collections.deque()
        for command in BaseCommand.get_commands_for_a_role(role):
            telegram_bot_command = BotCommand(
                str(command.command_type.value),
                command.command_description,
            )
            commands.append(telegram_bot_command)

        return list(commands)
