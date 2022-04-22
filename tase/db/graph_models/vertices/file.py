from typing import Optional

import pyrogram

from .base_vertex import BaseVertex


class File(BaseVertex):
    _vertex_name = 'files'

    file_unique_id: str

    @staticmethod
    def parse_from_audio(audio: 'pyrogram.types.Audio') -> Optional['File']:
        if audio is None:
            return None

        return File(
            key=audio.file_unique_id,
            file_unique_id=audio.file_unique_id,
        )
