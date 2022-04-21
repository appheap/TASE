from dataclasses import dataclass, field
from typing import Optional

import arrow
import pyrogram

from .base_vertex import BaseVertex


@dataclass
class Audio(BaseVertex):
    _vertex_name = 'audios'

    message_id: int
    message_caption: Optional['str']
    message_date: int

    # file_id: str # todo: is it necessary?
    file_unique_id: str
    duration: int
    performer: Optional['str']
    title: Optional['str']
    file_name: Optional['str']
    mime_type: Optional['str']
    file_size: int
    date: int

    def parse_for_graph(self) -> dict:
        super_dict = super(Audio, self).parse_for_graph()
        super_dict.update(
            {
                'message_id': self.message_id,
                'message_caption': self.message_caption,
                'message_date': self.message_date,
                'file_unique_id': self.file_unique_id,
                'duration': self.duration,
                'performer': self.performer,
                'title': self.title,
                'file_name': self.file_name,
                'mime_type': self.mime_type,
                'file_size': self.file_size,
                'date': self.date,
            }
        )
        return super_dict

    @staticmethod
    def parse_from_message(message: 'pyrogram.types.Message') -> Optional['Audio']:
        if not message or not message.audio:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{message.audio.file_unique_id}{message.chat.id}{message.message_id}'
        return Audio(
            id=None,
            key=key,
            rev=None,
            created_at=ts,
            modified_at=ts,
            message_id=message.message_id,
            message_caption=message.caption,
            message_date=message.date,
            file_unique_id=message.audio.file_unique_id,
            duration=message.audio.duration,
            performer=message.audio.performer,
            title=message.audio.title,
            file_name=message.audio.file_name,
            mime_type=message.audio.mime_type,
            file_size=message.audio.file_size,
            date=message.audio.date,
        )
