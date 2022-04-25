from typing import Optional

import pyrogram

from tase.utils import get_timestamp
from .base_vertex import BaseVertex


class Audio(BaseVertex):
    _vertex_name = 'audios'

    message_id: int
    message_caption: Optional[str]
    message_date: int

    # file_id: str # todo: is it necessary?
    file_unique_id: str
    duration: int
    performer: Optional[str]
    title: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: int
    date: int

    @staticmethod
    def get_key(message: 'pyrogram.types.Message'):
        return f'{message.audio.file_unique_id}:{message.chat.id}:{message.id}'

    @staticmethod
    def parse_from_message(message: 'pyrogram.types.Message') -> Optional['Audio']:
        if not message or not message.audio:
            return None

        key = Audio.get_key(message)
        return Audio(
            key=key,
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
