from hashlib import sha1
from typing import Optional

from .base_vertex import BaseVertex
from .user import User


class Query(BaseVertex):
    _vertex_name = 'queries'

    query: str
    query_date: int

    duration: float
    max_score: float
    total_hits: int
    total_rel: str

    @staticmethod
    def get_key(
            bot: 'User',
            from_user: 'User',
            query_date: int,
    ) -> Optional['str']:
        if bot is None or from_user is None or query_date is None:
            return None

        return f"{bot.key}:{from_user.key}:{sha1(str(query_date).encode('utf-8')).hexdigest()}"

    @staticmethod
    def parse_from_query(
            bot: 'User',
            from_user: 'User',
            query: 'str',
            query_date: int,
            query_metadata: dict
    ) -> Optional['Query']:
        if bot is None or from_user is None or query is None or query_date is None or query_metadata is None:
            return None

        key = Query.get_key(bot, from_user, query_date)
        if not key:
            return None

        return Query(
            key=key,
            query_date=query_date,
            query=query,
            duration=query_metadata.get('duration'),
            max_score=query_metadata.get('max_score') or 0,
            total_hits=query_metadata.get('total_hits'),
            total_rel=query_metadata.get('total_rel'),
        )
