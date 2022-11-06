from typing import Optional, Match

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButtonType
from .my_playlists_button import MyPlaylistsInlineButton
from ...inline import CustomInlineQueryResult


class BackToPlaylistsInlineButton(MyPlaylistsInlineButton):
    name = "back_to_playlists"
    type = InlineButtonType.BACK_TO_PLAYLISTS

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"
    is_inline = True

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)
        if chat_type != ChatType.BOT:
            result.set_results(
                [],
                count=True,
            )
        else:
            await MyPlaylistsInlineButton.on_inline_query(
                self,
                handler,
                result,
                from_user,
                client,
                telegram_inline_query,
                query_date,
                reg,
            )

        await result.answer_query()

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):
        await MyPlaylistsInlineButton.on_chosen_inline_query(
            self,
            handler,
            client,
            from_user,
            telegram_chosen_inline_result,
            reg,
        )
