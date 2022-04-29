from typing import Optional

import pyrogram

from .base_vertex import BaseVertex
from .user import User


class InlineQuery(BaseVertex):
    _vertex_name = 'inline_queries'

    query_id: str
    query: str
    offset: str
    chat_type: str

    query_date: int

    duration: float
    max_score: float
    total_hits: int
    total_rel: str

    @staticmethod
    def get_key(
            bot: 'User',
            inline_query: 'pyrogram.types.InlineQuery'
    ) -> Optional['str']:
        if bot is None or inline_query is None:
            return None
        return f'{bot.key}:{inline_query.id}'

    @staticmethod
    def parse_from_inline_query(
            bot: 'User',
            inline_query: 'pyrogram.types.InlineQuery',
            query_date: int,
            query_metadata: dict
    ) -> Optional['InlineQuery']:
        if bot is None or inline_query is None:
            return None

        key = InlineQuery.get_key(bot, inline_query)
        if not key:
            return None

        return InlineQuery(
            key=key,
            query_id=inline_query.id,
            query=inline_query.query,
            offset=inline_query.offset,
            chat_type=inline_query.chat_type.name,
            query_date=query_date,
            duration=query_metadata.get('duration'),
            max_score=query_metadata.get('max_score'),
            total_hits=query_metadata.get('total_hits'),
            total_rel=query_metadata.get('total_rel'),
        )
