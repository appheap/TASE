from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Query, InlineQuery, Hit


class HasHit(BaseEdge):
    """
    Connection from `Query` or `InlineQuery` to `Hit`
    """

    _collection_edge_name = 'has_hit'

    _from_vertex_collections = [Query, InlineQuery]
    _to_vertex_collections = [Hit]

    @staticmethod
    def parse_from_query_and_hit(
            query: 'Query',
            hit: 'Hit',
    ) -> Optional['HasHit']:
        if query is None or hit is None:
            return None

        key = f'{query.key}:{hit.key}'
        return HasHit(
            key=key,
            from_node=query,
            to_node=hit,
        )

    @staticmethod
    def parse_from_inline_query_and_hit(
            inline_query: 'InlineQuery',
            hit: 'Hit',
    ) -> Optional['HasHit']:
        if inline_query is None or hit is None:
            return None

        key = f'{inline_query.key}@{hit.key}'
        return HasHit(
            key=key,
            from_node=inline_query,
            to_node=hit,
        )
