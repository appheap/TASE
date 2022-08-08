from pydantic.types import Enum


class MentionSource(Enum):
    """
    In this class, all kinds of sources are listed which a mention is extracted from
    """
    UNKNOWN = 0

    MESSAGE_TEXT = 1
    "mention source is either a description or bio"

    FORWARDED_CHAT_USERNAME = 2
    "mention source is forwarded chat username"

    FORWARDED_CHAT_DESCRIPTION = 3
    "mention source is forwarded chat bio / description"

    AUDIO_TITLE = 4
    "mention source is audio file's title"

    AUDIO_PERFORMER = 5
    "mention source is audio file's performer"

    AUDIO_FILE_NAME = 6
    "mention source is audio file's name"
