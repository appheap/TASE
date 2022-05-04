from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, Query, InlineQuery
from ...elasticsearch_models.base_document import SearchMetaData


class Hit(BaseEdge):
    """
    Connection from `Query` or `InlineQuery` to `Audio`
    """

    _collection_edge_name = 'hit'

    _from_vertex_collections = [Query, InlineQuery]
    _to_vertex_collections = [Audio]

    rank: int
    score: float

    @staticmethod
    def parse_from_query_and_audio(
            query: 'Query',
            audio: 'Audio',
            search_metadata: 'SearchMetaData'
    ) -> Optional['Hit']:
        if query is None or audio is None:
            return None

        key = f'{query.key}:{audio.key}'
        return Hit(
            key=key,
            from_node=query,
            to_node=audio,
            rank=search_metadata.rank,
            score=search_metadata.score,
        )

    @staticmethod
    def parse_from_inline_query_and_audio(
            inline_query: 'InlineQuery',
            audio: 'Audio',
            search_metadata: 'SearchMetaData'
    ) -> Optional['Hit']:
        if inline_query is None or audio is None:
            return None

        key = f'{inline_query.key}:{audio.key}'
        return Hit(
            key=key,
            from_node=inline_query,
            to_node=audio,
            rank=search_metadata.rank,
            score=search_metadata.score,
        )
