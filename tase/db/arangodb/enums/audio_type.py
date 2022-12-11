from enum import Enum


class AudioType(Enum):
    NOT_ARCHIVED = 1
    """
    Audio is not archived and it's only been indexed. The audio document cache is available.
    """

    ARCHIVED = 2
    """
    Audio is archived and the archived version is available. The archived audio vertex and audio document cache are available.
    """

    UPLOADED = 3
    """
    Audio is uploaded rather than being indexed, The uploaded audio vertex and audio document cache are available.
    """

    SENT_BY_USERS = 4
    """
    Audio is sent to the bot by users and stored in the archive. The sent audio vertex and audio document cache are available.
    """
