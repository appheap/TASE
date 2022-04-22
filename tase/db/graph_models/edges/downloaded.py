from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import User, Download


@dataclass
class Downloaded(BaseEdge):
    """
    Connection from `User` to `Download`
    """

    _collection_edge_name = 'downloaded'

    @staticmethod
    def parse_from_user_and_download(user: 'User', download: 'Download') -> Optional['Downloaded']:
        if user is None or download is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{user.key}:{download.key}'
        return Downloaded(
            id=None,
            key=key,
            rev=None,
            from_node=user,
            to_node=download,
            created_at=ts,
            modified_at=ts,
        )
