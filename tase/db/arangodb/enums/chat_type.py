from __future__ import annotations

from enum import Enum
from typing import Optional

import pyrogram


class ChatType(Enum):
    UNKNOWN = 0

    PRIVATE = 1
    "Chat is a private chat with a user"

    BOT = 2
    "Chat is a private chat with a bot"

    GROUP = 3
    "Chat is a basic group"

    SUPERGROUP = 4
    "Chat is a supergroup"

    CHANNEL = 5
    "Chat is a channel"

    @staticmethod
    def parse_from_pyrogram(
        chat_type: pyrogram.enums.ChatType,
    ) -> Optional[ChatType]:
        """
        Parse the `ChatType` from pyrogram `chat_type`

        Parameters
        ----------
        chat_type : pyrogram.enums.ChatType
            Chat type of pyrogram chat object

        Returns
        -------
        ChatType, optional
            Parsed ChatType
        """
        if chat_type is None:
            return None

        return _from_pyrogram_mapping[chat_type.value]


_from_pyrogram_mapping = {
    pyrogram.enums.ChatType.PRIVATE.value: ChatType.PRIVATE,
    pyrogram.enums.ChatType.BOT.value: ChatType.BOT,
    pyrogram.enums.ChatType.GROUP.value: ChatType.GROUP,
    pyrogram.enums.ChatType.SUPERGROUP.value: ChatType.SUPERGROUP,
    pyrogram.enums.ChatType.CHANNEL.value: ChatType.CHANNEL,
}
