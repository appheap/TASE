from typing import Optional

import pyrogram
from pydantic.types import Enum


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
        chat_type: "pyrogram.enums.ChatType",
    ) -> Optional["ChatType"]:
        if chat_type is None:
            # fixme: how to avoid this?
            raise Exception("chat_type cannot be empty")

        return _from_pyrogram_mapping[chat_type.value]


_from_pyrogram_mapping = {
    pyrogram.enums.ChatType.PRIVATE.value: ChatType.PRIVATE,
    pyrogram.enums.ChatType.BOT.value: ChatType.BOT,
    pyrogram.enums.ChatType.GROUP.value: ChatType.GROUP,
    pyrogram.enums.ChatType.SUPERGROUP.value: ChatType.SUPERGROUP,
    pyrogram.enums.ChatType.CHANNEL.value: ChatType.CHANNEL,
}
