from enum import Enum


class ButtonActionType(Enum):
    CALLBACK = 0
    CURRENT_CHAT_INLINE = 1
    OTHER_CHAT_INLINE = 2
    OPEN_URL = 3
