from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import Audio


@dataclass
class ArchivedAudio(BaseEdge):
    """
    Connection from `Audio` to the archived `Audio`
    """

    @staticmethod
    def parse_from_audio_and_audio(audio: 'Audio', archived_audio: 'Audio') -> Optional['ArchivedAudio']:
        if audio is None or archived_audio is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        return ArchivedAudio(
            id=None,
            key=None,
            from_node=audio,
            to_node=archived_audio,
            created_at=ts,
            modified_at=ts,
        )
