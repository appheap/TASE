import collections
from typing import List, Optional

import pyrogram
from pydantic import BaseModel, Field

from .bot_command_type import BotCommandType
from ...my_logger import logger


class BaseCommand(BaseModel):
    command_type: BotCommandType = Field(default=BotCommandType.HELP)
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
        command = BaseCommand.get_command(
            bot_command_type if bot_command_type is not None else BotCommandType.get_from_message(message)
        )
        if command:
            db_from_user = handler.db.get_or_create_user(message.from_user)

            command.command_function(client, message, handler, db_from_user)

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
