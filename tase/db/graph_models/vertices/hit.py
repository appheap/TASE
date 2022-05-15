import secrets
from typing import Optional, Union

from arango.collection import VertexCollection

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

    download_url: Optional[str]

    @staticmethod
    def get_key(
            q: Union[Query, InlineQuery],
            audio: Audio,
    ) -> Optional[str]:
        if q is None or audio is None:
            return None

        return f'{q.key}:{audio.key}:{q.query_date}'

    @staticmethod
    def generate_download_url():
        while True:
            # todo: make sure the generated token is unique
            download_url = secrets.token_urlsafe(6)
            if download_url.find('-') == -1:
                break
        return download_url

    @staticmethod
    def parse_from_query_and_audio(
            query: 'Query',
            audio: 'Audio',
            search_metadata: 'SearchMetaData',
    ) -> Optional['Hit']:
        if query is None or audio is None:
            return None

        key = Hit.get_key(query, audio)
        download_url = Hit.generate_download_url()
        return Hit(
            key=key,
            rank=search_metadata.rank,
            score=search_metadata.score,
            query_date=query.query_date,
            download_url=download_url,
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
        download_url = Hit.generate_download_url()
        return Hit(
            key=key,
            rank=search_metadata.rank,
            score=search_metadata.score,
            query_date=inline_query.query_date,
            download_url=download_url,
        )

    @classmethod
    def find_by_download_url(cls, db: 'VertexCollection', download_url: str) -> Optional['Hit']:
        if db is None or download_url is None:
            return None

        cursor = db.find({'download_url': download_url})
        if cursor and len(cursor):
            return cls.parse_from_graph(cursor.pop())
        else:
            return None
