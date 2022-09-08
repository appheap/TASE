from typing import Optional

import pyrogram

from .base_vertex import BaseVertex
from .chat import ChatType
from .user import User
from ...enums import InlineQueryType
from ...helpers import ElasticQueryMetadata, InlineQueryMetadata


class Query(BaseVertex):
    _collection_name = "queries"

    query: str

    inline_metadata: Optional[InlineQueryMetadata]
    elastic_metadata: ElasticQueryMetadata

    @classmethod
    def parse_key(
        cls,
        bot: User,
        user: User,
        query_date: int,
    ) -> Optional[str]:
        if bot is None or user is None or query_date is None:
            return None
        return f"{bot.key}:{user.key}:{query_date}"

    @classmethod
    def parse(
        cls,
        bot: User,
        user: User,
        query: str,
        query_date: int,
        query_metadata: dict,
        # following parameters are intended to be used for `InlineQuery` rather than normal query.
        telegram_inline_query: pyrogram.types.InlineQuery,
        inline_query_type: InlineQueryType,
        next_offset: Optional[str],
    ) -> Optional["Query"]:
        if bot is None or user is None:
            return None

        key = cls.parse_key(bot, user, query_date)
        if key is None:
            return None

        metadata = ElasticQueryMetadata.parse(query_metadata)
        if metadata is None:
            return None

        if telegram_inline_query is not None:
            inline_metadata = InlineQueryMetadata(
                query_id=telegram_inline_query.id,
                chat_type=ChatType.parse_from_pyrogram(telegram_inline_query.chat_type),
                offset=telegram_inline_query.offset,
                next_offset=next_offset,
                type=inline_query_type,
            )
        else:
            inline_metadata = None

        return Query(
            key=key,
            query=query,
            inline_metadata=inline_metadata,
            elastic_metadata=metadata,
        )


class QueryMethods:
    pass
