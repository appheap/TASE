from re import Match
from typing import Optional

import pyrogram

from ..inline import CustomInlineQueryResult
from ...db import graph_models


class OnInlineQuery:
    def on_inline_query(
        self,
        handler: "BaseHandler",
        result: CustomInlineQueryResult,
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        inline_query: "pyrogram.types.InlineQuery",
        query_date: int,
        reg: Optional[Match] = None,
    ):
        raise NotImplementedError
