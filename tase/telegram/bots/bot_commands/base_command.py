import collections
from typing import List, Optional

import pyrogram
from pydantic import BaseModel, Field

from tase.db.graph_models.vertices import UserRole, User
from tase.my_logger import logger
from tase.utils import _trans
from .bot_command_type import BotCommandType


class BaseCommand(BaseModel):
    """
    This class is used as the base class for all other commands to inherit from.
    Any class who inherits from this class needs to implement
    :meth:`~tase.telegram.bots.bot_commands.BaseCommand.command_function` method.


    Attributes
    ----------
    command_type : BotCommandType
        Type of this command
    required_role_level : UserRole
        Role level required to execute this command
    number_of_required_arguments : int
        Number of arguments necessary to run this command
    """

    command_type: BotCommandType = Field(default=BotCommandType.HELP)
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
    ) -> Optional["BaseCommand"]:
        if bot_command_type is None:
            return None
        return cls._registry.get(str(bot_command_type.value), None)

    @classmethod
    def run_command(
        cls,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        bot_command_type: Optional[BotCommandType] = None,
    ) -> None:
        if client is None or message is None or handler is None or message.from_user is None:
            return

        command = BaseCommand.get_command(
            bot_command_type if bot_command_type is not None else BotCommandType.get_from_message(message)
        )
        if command:
            if len(message.command) - 1 < command.number_of_required_arguments:
                # todo: translate me
                message.reply_text(
                    "Not enough arguments are provided to run this command",
                    quote=True,
                    disable_web_page_preview=True,
                )
                return

            db_from_user: User = handler.db.get_or_create_user(message.from_user)
            if db_from_user is None:
                raise Exception(f"Could not get/create user vertex from: {message.from_user}")

            # check if the user has permission to execute this command
            if db_from_user.role.value >= command.required_role_level.value:
                try:
                    command.command_function(client, message, handler, db_from_user)
                except NotImplementedError:
                    pass
                except Exception as e:
                    logger.exception(e)
            else:
                # todo: log users who query these commands without having permission
                message.reply_text(
                    _trans(
                        "You don't have the required permission to execute this command!",
                        db_from_user.chosen_language_code,
                    ),
                    quote=True,
                    disable_web_page_preview=True,
                )

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
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
            if bot_command_type not in (BotCommandType.INVALID, BotCommandType.UNKNOWN):
                command = BaseCommand.get_command(bot_command_type)
                if command:
                    lst.append(str(command.command_type.value))

        return list(lst)
