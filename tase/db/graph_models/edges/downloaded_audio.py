from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import Download, Audio


@dataclass
class DownloadedAudio(BaseEdge):
    """
    Connection from `Download` to `Audio`
    """

    _collection_edge_name = 'downloaded_audio'

    @staticmethod
    def parse_from_download_and_audio(download: 'Download', audio: 'Audio') -> Optional['DownloadedAudio']:
        if download is None or audio is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{download.key}:{audio.key}'
        return DownloadedAudio(
            id=None,
            key=key,
            rev=None,
            from_node=download,
            to_node=audio,
            created_at=ts,
            modified_at=ts,
        )
