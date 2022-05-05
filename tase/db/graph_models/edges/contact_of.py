from typing import Optional

from .base_edge import BaseEdge
from ..vertices import User


class ContactOf(BaseEdge):
    """
    Connection from a `User` to another `User`.
    """

    _collection_edge_name = 'contact_of'

    _from_vertex_collections = [User]
    _to_vertex_collections = [User]

    @staticmethod
    def parse_from_user_and_user(from_user: 'User', to_user: 'User') -> Optional['ContactOf']:
        if from_user is None or to_user is None:
            return None

        key = f'{from_user.key}@{to_user.key}'
        return ContactOf(
            key=key,
            from_node=from_user,
            to_node=to_user,
        )
