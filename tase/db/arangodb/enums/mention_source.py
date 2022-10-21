from __future__ import annotations

from enum import Enum


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
    "mention source is audio file title"

    AUDIO_PERFORMER = 5
    "mention source is audio file performer"

    AUDIO_FILE_NAME = 6
    "mention source is audio file name"

    DOCUMENT_FILE_NAME = 7
    "mention source is document file name"

    INLINE_KEYBOARD_TEXT = 8
    "mention source is in the message inline keyboard button text"

    INLINE_KEYBOARD_TEXT_LINK = 9
    "mention source is in the message inline keyboard button text link"

    @classmethod
    def is_direct_mention(
        cls,
        mention_source: MentionSource,
    ) -> bool:
        return is_direct_mentions_dict[mention_source]


is_direct_mentions_dict = {
    MentionSource.MESSAGE_TEXT: True,
    MentionSource.FORWARDED_CHAT_USERNAME: True,
    MentionSource.FORWARDED_CHAT_DESCRIPTION: True,
    MentionSource.AUDIO_TITLE: False,
    MentionSource.AUDIO_PERFORMER: False,
    MentionSource.AUDIO_FILE_NAME: False,
    MentionSource.DOCUMENT_FILE_NAME: False,
}
