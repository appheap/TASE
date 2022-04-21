from dataclasses import dataclass
from typing import Optional

import arrow
import pyrogram

from .base_vertex import BaseVertex


@dataclass
class File(BaseVertex):
    _vertex_name = 'files'

    file_unique_id: str

    def parse_for_graph(self) -> dict:
        super_dict = super(File, self).parse_for_graph()
        super_dict.update(
            {
                'file_unique_id': self.file_unique_id,
            }
        )

        return super_dict

    @staticmethod
    def parse_from_audio(audio: 'pyrogram.types.Audio') -> Optional['File']:
        if audio is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        return File(
            id=None,
            key=audio.file_unique_id,
            rev=None,
            created_at=ts,
            modified_at=ts,
            file_unique_id=audio.file_unique_id,
        )
