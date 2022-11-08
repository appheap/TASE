import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler


class OnCallbackQuery:
    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        raise NotImplementedError
