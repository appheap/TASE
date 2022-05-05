from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Query, InlineQuery, QueryKeyword


class ToQueryKeyword(BaseEdge):
    """
    Connection from `Query` or `InlineQuery` to `QueryKeyword`
    """

    _collection_edge_name = 'to_query_keyword'

    _from_vertex_collections = [Query, InlineQuery]
    _to_vertex_collections = [QueryKeyword]

    @staticmethod
    def parse_from_query_and_query_keyword(
            query: 'Query',
            query_keyword: 'QueryKeyword',
    ) -> Optional['ToQueryKeyword']:
        if query is None or query_keyword is None:
            return None

        key = f'{query.key}@{query_keyword.key}'
        return ToQueryKeyword(
            key=key,
            from_node=query,
            to_node=query_keyword,
        )

    @staticmethod
    def parse_from_inline_query_and_query_keyword(
            inline_query: 'InlineQuery',
            query_keyword: 'QueryKeyword'
    ) -> Optional['ToQueryKeyword']:
        if inline_query is None or query_keyword is None:
            return None

        key = f'{inline_query.key}@{query_keyword.key}'
        return ToQueryKeyword(
            key=key,
            from_node=inline_query,
            to_node=query_keyword,
        )
