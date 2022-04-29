from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, Query, InlineQuery
from ...elasticsearch_models.base_document import SearchMetaData


class Hit(BaseEdge):
    """
    Connection from `Query` or `InlineQuery` to `Audio`
    """

    _collection_edge_name = 'hit'

    _from_vertex_collections = [Query._vertex_name, InlineQuery._vertex_name]
    _to_vertex_collections = [Audio._vertex_name]

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
