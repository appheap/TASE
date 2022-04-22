from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import Download, User


@dataclass
class DownloadedFromBot(BaseEdge):
    """
    Connection from `Download` to `User`
    """

    _collection_edge_name = 'downloaded_from_bot'

    @staticmethod
    def parse_from_download_and_user(download: 'Download', user: 'User') -> Optional['DownloadedFromBot']:
        if download is None or user is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{download.key}:{user.key}'
        return DownloadedFromBot(
            id=None,
            key=key,
            rev=None,
            from_node=download,
            to_node=user,
            created_at=ts,
            modified_at=ts,
        )
