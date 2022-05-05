from typing import Optional, Union

from .base_vertex import BaseVertex
from .audio import Audio
from .query import Query
from .inline_query import InlineQuery
from ...elasticsearch_models.base_document import SearchMetaData


class Hit(BaseVertex):
    _vertex_name = 'hits'

    rank: int
    score: float
    query_date: int

    @staticmethod
    def get_key(
            q: Union[Query, InlineQuery],
            audio: Audio,
    ) -> Optional[str]:
        if q is None or audio is None:
            return None

        return f'{q.key}:{audio.key}:{q.query_date}'

    @staticmethod
    def parse_from_query_and_audio(
            query: 'Query',
            audio: 'Audio',
            search_metadata: 'SearchMetaData',
    ) -> Optional['Hit']:
        if query is None or audio is None:
            return None

        key = Hit.get_key(query, audio)
        return Hit(
            key=key,
            rank=search_metadata.rank,
            score=search_metadata.score,
            query_date=query.query_date,
        )

    @staticmethod
    def parse_from_inline_query_and_audio(
            inline_query: 'InlineQuery',
            audio: 'Audio',
            search_metadata: 'SearchMetaData',
    ) -> Optional['Hit']:
        if inline_query is None or audio is None:
            return None

        key = Hit.get_key(inline_query, audio)
        return Hit(
            key=key,
            rank=search_metadata.rank,
            score=search_metadata.score,
            query_date=inline_query.query_date,
        )
