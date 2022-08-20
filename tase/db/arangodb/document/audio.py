from typing import Union, Optional

import pyrogram

from tase.my_logger import logger
from .base_document import BaseDocument
from ... import elasticsearch_models


class Audio(BaseDocument):
    _collection_name = "doc_audios"
    schema_version = 1

    chat_id: int
    message_id: int

    file_id: str
    file_unique_id: str

    @classmethod
    def parse_key(
        cls,
        input_arg: Union[pyrogram.types.Message, elasticsearch_models.Audio],
        telegram_client_id: int,
    ) -> Optional[str]:
        if isinstance(input_arg, pyrogram.types.Message):
            telegram_message = input_arg
            if telegram_message.audio:
                _audio = telegram_message.audio
            elif telegram_message.document:
                _audio = telegram_message.document
            else:
                raise ValueError("Unexpected value for `message`: nor audio nor document")
            return f"{str(telegram_client_id)}:{_audio.file_unique_id}:{telegram_message.chat.id}:{telegram_message.id}"

        elif isinstance(input_arg, elasticsearch_models.Audio):
            audio = input_arg
            return f"{str(telegram_client_id)}:{audio.file_unique_id}:{audio.chat_id}:{audio.message_id}"
        else:
            # this not a valid instance
            raise ValueError("This is not valid instance")

    @classmethod
    def parse(
        cls,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ) -> Optional["Audio"]:
        try:
            if telegram_message.audio:
                _audio = telegram_message.audio
            elif telegram_message.document:
                _audio = telegram_message.document
            else:
                return None

            key = Audio.parse_key(telegram_message, telegram_client_id)
        except ValueError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        else:
            if key is None:
                return None

            return Audio(
                key=key,
                chat_id=telegram_message.chat.id,
                message_id=telegram_message.id,
                file_id=_audio.file_id,
                file_unique_id=_audio.file_unique_id,
            )

        return None


class AudioMethods:
    pass
