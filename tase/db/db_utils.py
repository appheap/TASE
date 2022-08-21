from typing import Tuple, Union, Optional

import pyrogram

from tase.db.arangodb.helpers import TelegramAudioType


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
