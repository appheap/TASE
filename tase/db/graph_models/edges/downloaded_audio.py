from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge


@dataclass
class DownloadedAudio(BaseEdge):
    """
    Connection from `Download` to `Audio`
    """

    @staticmethod
    def parse_from_download_and_audio(download: '', audio: '') -> Optional['DownloadedAudio']:
        if download is None or audio is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        return DownloadedAudio(
            id=None,
            key=None,
            from_node=download,
            to_node=audio,
            created_at=ts,
            modified_at=ts,
        )
