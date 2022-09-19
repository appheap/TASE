from .tase_error import TASEError


class TelegramMessageWithNoAudio(TASEError):
    """Telegram Message does not contain any kind of audio file"""

    MESSAGE = """`Message` object `{}` ID from chat `{}` does not have any audio file"""
