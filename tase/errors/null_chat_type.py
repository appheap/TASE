from .tase_error import TASEError


class NullChatType(TASEError):
    """Chat type of `Chat` object from pyrogram is `None`"""

    MESSAGE = "Chat type of `Chat` object from pyrogram is `None`"
