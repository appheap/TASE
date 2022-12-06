from typing import Tuple, Union, Optional

import pyrogram

from tase.db.arangodb.enums import TelegramAudioType


def get_telegram_message_media_type(
    telegram_message: pyrogram.types.Message,
) -> Tuple[Optional[Union[pyrogram.types.Audio, pyrogram.types.Document]], TelegramAudioType]:
    if telegram_message.media is None:
        audio = None
        audio_type = TelegramAudioType.NON_AUDIO
    else:
        if telegram_message.audio:
            audio = telegram_message.audio
            audio_type = TelegramAudioType.AUDIO_FILE

        elif telegram_message.document:
            if telegram_message.document.mime_type.startswith("audio"):
                audio = telegram_message.document
                audio_type = TelegramAudioType.AUDIO_DOCUMENT_FILE
            else:
                audio = None
                audio_type = TelegramAudioType.NON_AUDIO

        else:
            audio = None
            audio_type = TelegramAudioType.NON_AUDIO

    return audio, audio_type


def parse_audio_key(
    telegram_message: pyrogram.types.Message,
    chat_id: int,
) -> Optional[str]:
    """
    Parse the `key` from the given `telegram_message` argument

    Parameters
    ----------
    telegram_message : pyrogram.types.Message
        Telegram message to parse the key from
    chat_id : int
        Chat ID this message belongs to.

    Returns
    -------
    str, optional
        Parsed key if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

    """
    if telegram_message is None or chat_id is None:
        return None
    return f"{chat_id}:{telegram_message.id}"


def parse_audio_key_from_message_id(
    telegram_message_id: int,
    chat_id: int,
) -> Optional[str]:
    """
    Parse the `key` from the given `telegram_message` argument

    Parameters
    ----------
    telegram_message_id : int
        Telegram message id to parse the key from
    chat_id : int
        Chat ID this message belongs to.

    Returns
    -------
    str, optional
        Parsed key if the parsing was successful, otherwise return `None` if the `telegram_message` is `None`.

    """
    if telegram_message_id is None or chat_id is None:
        return None
    return f"{chat_id}:{telegram_message_id}"


forbidden_mime_types = (
    "audio/aac",
    "audio/AAC",
    "audio/x-flac",
    "audio/flac",
    "audio/MP3",
    "audio/m4a",
    "audio/mpeg3",
    "audio/x-wav",
    "audio/wav",
    "audio/ogg",
    "audio/x-vorbis+ogg",
    "audio/x-opus+ogg",
)

valid_mime_types_for_for_inline_search = (
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
)


def is_audio_valid_for_inline(
    audio: Union[pyrogram.types.Audio, pyrogram.types.Document],
    audio_type: TelegramAudioType,
) -> bool:
    title = getattr(audio, "title", None)
    if title is None or not len(title):
        return False
    if audio_type != TelegramAudioType.AUDIO_FILE:
        return False
    if audio.mime_type is None:
        return False
    if audio.mime_type in forbidden_mime_types or audio.mime_type not in valid_mime_types_for_for_inline_search:
        return False

    return True
