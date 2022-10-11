from __future__ import annotations

from enum import Enum

import pyrogram


class BotCommandType(Enum):
    UNKNOWN = "unknown"
    INVALID = "invalid"
    BASE = "base"

    # commands intended for testing purposes
    DUMMY = "dummy"

    # general commands
    START = "start"
    HOME = "home"
    HELP = "help"
    LANGUAGE = "lang"
    CANCEL = "cancel"

    # admin/creator commands
    ADD_CHANNEL = "add_channel"
    PROMOTE_USER = "promote_user"
    DEMOTE_USER = "demote_user"
    INDEX_CHANNEL = "index_channel"
    SHUTDOWN_SYSTEM = "shutdown_system"
    EXTRACT_USERNAMES = "extract_usernames"
    CHECK_USERNAMES = "check_usernames"

    @classmethod
    def get_from_message(
        cls,
        message: pyrogram.types.Message,
    ) -> BotCommandType:
        if message is None or message.command is None or not len(message.command):
            return BotCommandType.INVALID

        command_string = message.command[0].lower()

        for bot_command_type in list(BotCommandType):
            if str(bot_command_type.value) == command_string:
                return bot_command_type

        return BotCommandType.INVALID
