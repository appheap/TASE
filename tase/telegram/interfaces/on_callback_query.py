import pyrogram

from ...db import graph_models


class OnCallbackQuery:
    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        raise NotImplementedError
