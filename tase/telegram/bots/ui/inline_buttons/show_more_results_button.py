from typing import Optional, Match

import pyrogram

from tase.common.utils import _trans, emoji, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType
from ...inline import CustomInlineQueryResult, InlineSearch


class ShowMoreResultsInlineButton(InlineButton):
    type = InlineButtonType.SHOW_MORE_RESULTS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "more"

    s_more_results = _trans("More results")
    text = f"{s_more_results} | {emoji._plus}"

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
        from tase.telegram.bots.ui.inline_buttons.common import get_query_hash

        query_date = get_now_timestamp()
        from_user = await handler.db.graph.get_interacted_user(telegram_inline_query.from_user)

        # remove the command section from the original query to be like a normal inline query.
        command = reg.group("command")
        query = telegram_inline_query.query[telegram_inline_query.query.find(command) + len(command) :].strip()
        telegram_inline_query.query = query
        res = CustomInlineQueryResult(telegram_inline_query)

        q_split = query.split("\u200c")
        if len(q_split) == 2:
            given_query_hash, query = q_split

            given_query_hash = given_query_hash.strip()
            real_query_hash = get_query_hash(query)

            if res.is_first_page() and given_query_hash == real_query_hash:
                # if this is the first time this query is made, then the first 10 results should be skipped since it is already shown in the non-inline search
                # results.
                res.from_ = 10
            else:
                if given_query_hash != real_query_hash:
                    # query hash is invalid, user have changed the original query.
                    pass

            # remove the query hash section from the query string.
            telegram_inline_query.query = query

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
