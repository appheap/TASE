from typing import Optional

import pyrogram
from pydantic import Field
from pydantic.types import Enum

from .base_vertex import BaseVertex
from .chat import ChatType
from .user import User


class InlineQueryType(Enum):
    UNKNOWN = 0
    SEARCH = 1
    COMMAND = 2


class InlineQuery(BaseVertex):
    _vertex_name = "inline_queries"

    query_id: str
    query: str
    offset: str
    chat_type: ChatType

    query_date: int

    next_offset: Optional[str]

    duration: float
    max_score: float
    total_hits: int
    total_rel: str

    type: InlineQueryType = Field(default=InlineQueryType.SEARCH)

    @staticmethod
    def get_key(
        bot: "User",
        inline_query: "pyrogram.types.InlineQuery",
    ) -> Optional["str"]:
        if bot is None or inline_query is None:
            return None
        return f"{bot.key}:{inline_query.from_user.id}:{inline_query.id}"

    @staticmethod
    def parse_from_inline_query(
        bot: "User",
        inline_query: "pyrogram.types.InlineQuery",
        inline_query_type: InlineQueryType,
        query_date: int,
        query_metadata: dict,
        next_offset: Optional[str],
    ) -> Optional["InlineQuery"]:
        if bot is None or inline_query is None or inline_query_type is None:
            return None

        key = InlineQuery.get_key(
            bot,
            inline_query,
        )
        if not key:
            return None

        return InlineQuery(
            key=key,
            type=inline_query_type,
            query_id=inline_query.id,
            query=inline_query.query,
            offset=inline_query.offset,
            chat_type=ChatType.parse_from_pyrogram(inline_query.chat_type),
            query_date=query_date,
            duration=query_metadata.get("duration"),
            max_score=query_metadata.get("max_score") or 0,
            total_hits=query_metadata.get("total_hits"),
            total_rel=query_metadata.get("total_rel"),
            next_offset=next_offset,
        )
