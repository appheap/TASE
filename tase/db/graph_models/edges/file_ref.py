from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import File, Audio


@dataclass
class FileRef(BaseEdge):
    """
    Connection from `Audio` to `File`
    """

    _collection_edge_name = 'file_ref'

    @staticmethod
    def parse_from_audio_and_file(audio: Audio, file: File) -> Optional['FileRef']:
        if audio is None or file is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f"{audio.key}:{file.key}"
        return FileRef(
            id=None,
            key=key,
            from_node=audio,
            to_node=file,
            created_at=ts,
            modified_at=ts,
        )
