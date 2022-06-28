from re import Match

import pyrogram

from ...db import graph_models


class OnChosenInlineQuery:
    def on_chosen_inline_query(
        self,
        handler: "BaseHandler",
        client: "pyrogram.Client",
        db_from_user: graph_models.vertices.User,
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
        reg: Match,
    ):
        raise NotImplementedError
