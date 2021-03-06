from typing import Optional

from .base_edge import BaseEdge
from ..vertices import InlineQuery, User, Query


class ToBot(BaseEdge):
    """
    Connection from `InlineQuery` to `User`
    """

    _collection_edge_name = 'to_bot'

    _from_vertex_collections = [InlineQuery, Query]
    _to_vertex_collections = [User]

    @staticmethod
    def parse_from_inline_query_and_user(inline_query: 'InlineQuery', user: 'User') -> Optional['ToBot']:
        if inline_query is None or user is None:
            return None

        key = f'{inline_query.key}@{user.key}'
        return ToBot(
            key=key,
            from_node=inline_query,
            to_node=user,
        )

    @staticmethod
    def parse_from_query_and_user(query: 'Query', user: 'User') -> Optional['ToBot']:
        if query is None or user is None:
            return None

        key = f'{query.key}@{user.key}'
        return ToBot(
            key=key,
            from_node=query,
            to_node=user,
        )
