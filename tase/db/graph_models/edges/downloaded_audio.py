from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Download, Audio


class DownloadedAudio(BaseEdge):
    """
    Connection from `Download` to `Audio`
    """

    _collection_edge_name = 'downloaded_audio'

    _from_vertex_collections = [Download._vertex_name]
    _to_vertex_collections = [Audio._vertex_name]

    @staticmethod
    def parse_from_download_and_audio(download: 'Download', audio: 'Audio') -> Optional['DownloadedAudio']:
        if download is None or audio is None:
            return None

        key = f'{download.key}:{audio.key}'
        return DownloadedAudio(
            key=key,
            from_node=download,
            to_node=audio,
        )
