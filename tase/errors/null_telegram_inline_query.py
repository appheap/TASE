from .tase_error import TASEError


class NullTelegramInlineQuery(TASEError):
    """Telegram InlineQuery object cannot be None"""

    MESSAGE = """Telegram InlineQuery object cannot be None"""
