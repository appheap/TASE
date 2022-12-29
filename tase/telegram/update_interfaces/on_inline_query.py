from typing import Optional

import pyrogram

from tase.db.arangodb import graph as graph_models

# from tase.telegram.bots.inline import CustomInlineQueryResult
# from tase.telegram.bots.ui.base import InlineButtonData
# from tase.telegram.update_handlers.base import BaseHandler


class OnInlineQuery:
    async def on_inline_query(
        self,
        handler: "BaseHandler",
        result: "CustomInlineQueryResult",
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        inline_button_data: Optional["InlineButtonData"] = None,
    ):
        raise NotImplementedError
