from typing import Optional

import pyrogram

from .base_document import BaseDocument
from ...utils import get_timestamp


class Audio(BaseDocument):
    _index_name = 'audios_index'

    message_id: int
    message_caption: Optional[str]
    message_date: int

    file_unique_id: str
    duration: int
    performer: Optional[str]
    title: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: int
    date: int

    @staticmethod
    def get_id(message: 'pyrogram.types.Message'):
        return f'{message.audio.file_unique_id}:{message.chat.id}:{message.id}'

    @classmethod
    def parse_from_message(cls, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None:
            return None

        return Audio(
            id=cls.get_id(message),
            message_id=message.id,
            message_caption=message.caption,
            message_date=get_timestamp(message.date),
            file_unique_id=message.audio.file_unique_id,
            duration=message.audio.duration,
            performer=message.audio.performer,
            title=message.audio.title,
            file_name=message.audio.file_name,
            mime_type=message.audio.mime_type,
            file_size=message.audio.file_size,
            date=get_timestamp(message.audio.date),
        )
