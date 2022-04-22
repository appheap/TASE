from dataclasses import dataclass
from typing import Optional

import arrow

from .base_edge import BaseEdge
from ..vertices import User


@dataclass
class ContactOf(BaseEdge):
    """
    Connection from a `User` to another `User`.
    """

    _collection_edge_name = 'contact_of'

    @staticmethod
    def parse_from_user_and_user(from_user: 'User', to_user: 'User') -> Optional['ContactOf']:
        if from_user is None or to_user is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        key = f'{from_user.key}:{to_user.key}'
        return ContactOf(
            id=None,
            key=key,
            rev=None,
            from_node=from_user,
            to_node=to_user,
            created_at=ts,
            modified_at=ts,
        )
