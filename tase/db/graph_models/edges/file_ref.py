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

    @staticmethod
    def parse_from_audio_and_file(audio: Audio, file: File) -> Optional['FileRef']:
        if audio is None or file is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        return FileRef(
            id=None,
            key=None,
            from_node=audio,
            to_node=file,
            created_at=ts,
            modified_at=ts,
        )

