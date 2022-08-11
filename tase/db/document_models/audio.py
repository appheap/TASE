from typing import Optional

import pyrogram

from .base_document import BaseDocument
from .. import elasticsearch_models


class Audio(BaseDocument):
    _doc_collection_name = "doc_audios"

    chat_id: int
    message_id: int

    file_id: str
    file_unique_id: str

    @staticmethod
    def get_key(
        message: "pyrogram.types.Message",
        telegram_client_id: int,
    ):
        if message.audio:
            _audio = message.audio
        elif message.document:
            _audio = message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")
        return f"{str(telegram_client_id)}:{_audio.file_unique_id}:{message.chat.id}:{message.id}"

    @staticmethod
    def get_key_from_audio(
        audio: "elasticsearch_models.Audio",
        telegram_client_id: int,
    ):
        return f"{str(telegram_client_id)}:{audio.file_unique_id}:{audio.chat_id}:{audio.message_id}"

    @staticmethod
    def parse_from_message(
        message: "pyrogram.types.Message",
        telegram_client_id: int,
    ) -> Optional["Audio"]:
        if not message or (message.audio is None and message.document is None) or telegram_client_id is None:
            return None

        key = Audio.get_key(message, telegram_client_id)

        if message.audio:
            _audio = message.audio
        elif message.document:
            _audio = message.document
        else:
            raise ValueError("Unexpected value for `message`: nor audio nor document")

        return Audio(
            key=key,
            chat_id=message.chat.id,
            message_id=message.id,
            file_id=_audio.file_id,
            file_unique_id=_audio.file_unique_id,
        )
