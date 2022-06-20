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
    def get_key(message: "pyrogram.types.Message", telegram_client_id: int):
        return f"{str(telegram_client_id)}:{message.audio.file_unique_id}:{message.chat.id}:{message.id}"

    @staticmethod
    def get_key_from_audio(
        audio: "elasticsearch_models.Audio", telegram_client_id: int
    ):
        return f"{str(telegram_client_id)}:{audio.file_unique_id}:{audio.chat_id}:{audio.message_id}"

    @staticmethod
    def parse_from_message(
        message: "pyrogram.types.Message", telegram_client_id: int
    ) -> Optional["Audio"]:
        if not message or not message.audio or telegram_client_id is None:
            return None

        key = Audio.get_key(message, telegram_client_id)
        return Audio(
            key=key,
            chat_id=message.chat.id,
            message_id=message.id,
            file_id=message.audio.file_id,
            file_unique_id=message.audio.file_unique_id,
        )
