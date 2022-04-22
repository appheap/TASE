from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Download, User


class DownloadedFromBot(BaseEdge):
    """
    Connection from `Download` to `User`
    """

    _collection_edge_name = 'downloaded_from_bot'

    @staticmethod
    def parse_from_download_and_user(download: 'Download', user: 'User') -> Optional['DownloadedFromBot']:
        if download is None or user is None:
            return None

        key = f'{download.key}:{user.key}'
        return DownloadedFromBot(
            key=key,
            from_node=download,
            to_node=user,
        )
