from typing import Optional

import pyrogram

from .base_document import BaseDocument
from ...utils import get_timestamp


class Audio(BaseDocument):
    _index_name = 'audios_index'
    _mappings = {
        "properties": {
            "created_at": {
                "type": "long"
            },
            "modified_at": {
                "type": "long"
            },
            "chat_id": {
                "type": "long"
            },
            "message_id": {
                "type": "long"
            },
            "message_caption": {
                "type": "text"
            },
            "message_date": {
                "type": "date"
            },
            "file_unique_id": {
                "type": "keyword"
            },
            "duration": {
                "type": "integer"
            },
            "performer": {
                "type": "text"
            },
            "title": {
                "type": "text"
            },
            "file_name": {
                "type": "text"
            },
            "mime_type": {
                "type": "keyword"
            },
            "file_size": {
                "type": "integer"
            },
            "date": {
                "type": "date"
            },
        }
    }

    _search_fields = ['performer', 'file_name', 'message_caption', 'title']

    chat_id: int
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
            chat_id=message.chat.id,
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
