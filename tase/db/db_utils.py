from typing import Tuple, Union, Optional

import pyrogram

from tase.db.arangodb.enums import TelegramAudioType
from tase.errors import TelegramMessageWithNoAudio


def get_telegram_message_media_type(
    telegram_message: pyrogram.types.Message,
) -> Tuple[Optional[Union[pyrogram.types.Audio, pyrogram.types.Document]], TelegramAudioType]:
    """
    Get media type of the given telegram message along with included telegram `Audio` or `Document` object if it has any.

    Parameters
    ----------
    telegram_message : pyrogram.types.Message
        Telegram message to extract the `Audio` from.

    Returns
    -------
    tuple
        A tuple of `Audio` or `Document` and the type of the telegram audio in the given message.

    """
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


    Raises
    ------
    TelegramMessageWithNoAudio
        If `telegram_message` argument does not contain any valid audio file.
    """
    if telegram_message is None or chat_id is None:
        return None

    audio, telegram_audio_type = get_telegram_message_media_type(telegram_message)
    if audio is None or telegram_audio_type == TelegramAudioType.NON_AUDIO:
        raise TelegramMessageWithNoAudio(telegram_message.id, chat_id)

    return f"{chat_id}:{telegram_message.id}:{audio.file_unique_id}"


def parse_thumbnail_key(archive_chat_id: int, archive_message_id: int) -> Optional[str]:
    if archive_chat_id is None or archive_message_id is None:
        return None

    return f"{archive_chat_id}:{archive_message_id}"


def parse_thumbnail_document_key(
    telegram_client_id: int,
    archive_chat_id: int,
    archive_message_id: int,
) -> Optional[str]:
    """
    Parse the thumbnail document key from the given arguments.

    Parameters
    ----------
    telegram_client_id : int
        ID of the telegram client uploading this thumbnail.
    archive_chat_id : int
        ID of the chat this thumbnail message is archived in.
    archive_message_id :
        ID of the message this thumbnail message is archived in.

    Returns
    -------
    str, optional
        Parsed key of the thumbnail document.
    """
    if telegram_client_id is None or archive_chat_id is None or archive_message_id is None:
        return None
    return f"{telegram_client_id}:{archive_chat_id}:{archive_message_id}"


def parse_audio_document_key(
    telegram_client_id: int,
    chat_id: int,
    telegram_message: pyrogram.types.Message,
) -> Optional[str]:
    """
    Parse the `key` from the given `telegram_message` argument

    Parameters
    ----------
    telegram_client_id : int
        ID of the telegram client which has seen this message.
    chat_id : int
        Chat ID this message belongs to.
    telegram_message : pyrogram.types.Message
        Telegram message to parse the key from

    Returns
    -------
    str, optional
        Parsed key if the parsing was successful, otherwise return `None`.

    Raises
    ------
    TelegramMessageWithNoAudio
        If `telegram_message` argument does not contain any valid audio file.
    """
    if telegram_client_id is None or telegram_message is None or chat_id is None:
        return None

    audio, telegram_audio_type = get_telegram_message_media_type(telegram_message)

    if audio is None or telegram_audio_type == TelegramAudioType.NON_AUDIO:
        raise TelegramMessageWithNoAudio(telegram_message.id, chat_id)

    return f"{telegram_client_id}:{chat_id}:{telegram_message.id}:{audio.file_unique_id}"


def parse_audio_document_key_from_raw_attributes(
    telegram_client_id: int,
    chat_id: int,
    telegram_message_id: int,
    file_unique_id: str,
) -> Optional[str]:
    """
    Parse the `key` from the given raw parameters.

    Parameters
    ----------
    telegram_client_id : int
        ID of the telegram client which has seen this message.
    chat_id : int
        Chat ID this message belongs to.
    telegram_message_id : int
        Telegram message ID to parse the key from
    file_unique_id : str
        File unique ID to parse the key from.
    Returns
    -------
    str, optional
        Parsed key if the parsing was successful, otherwise return `None`.
    """
    if telegram_client_id is None or telegram_message_id is None or chat_id is None or not file_unique_id:
        return None

    return f"{telegram_client_id}:{chat_id}:{telegram_message_id}:{file_unique_id}"


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
