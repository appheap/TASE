from typing import Optional, Match

import pyrogram

from tase.common.utils import _trans, emoji, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButtonType, InlineButton
from ...inline import CustomInlineQueryResult, InlineSearch


class ShowMoreResultsInlineButton(InlineButton):
    name = "show_more_results"
    type = InlineButtonType.SHOW_MORE_RESULTS

    s_more_results = _trans("More results")
    text = f"{s_more_results} | {emoji._plus}"
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
        query_date = get_now_timestamp()
        from_user = await handler.db.graph.get_interacted_user(telegram_inline_query.from_user)

        res = CustomInlineQueryResult(telegram_inline_query)
        if not res.is_first_page():
            # if this is the first time this query is made, then the first 10 results should be skipped since it is already shown in the non-inline search
            # results.
            res.from_ = 10

        # remove the command section from the original query to be like a normal inline query.
        command = reg.group("command")
        telegram_inline_query.query = telegram_inline_query.query[telegram_inline_query.query.find(command) + len(command) :].strip()

        await InlineSearch.on_inline_query(
            handler,
            res,
            from_user,
            client,
            telegram_inline_query,
            query_date,
        )

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):
        # Since the items sent to user are download URLs which is handled by `download_handler`, there is no need for it anymore.
        pass
