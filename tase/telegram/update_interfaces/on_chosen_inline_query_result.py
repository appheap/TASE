import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler


class OnChosenInlineQuery:
    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: "InlineButtonData",
        inline_item_info: "InlineItemInfo",
    ):
        raise NotImplementedError
