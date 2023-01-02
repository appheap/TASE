from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData, InlineItemType
from ..inline_items.item_info import AudioItemInfo
from ...inline import CustomInlineQueryResult, InlineSearch


class ShowMoreResultsButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.SHOW_MORE_RESULTS

    query_hash: str
    query: str

    @classmethod
    def generate_data(cls, query_hash: str, query: str) -> Optional[str]:
        return f"${cls.get_type_value()}|{query_hash}| {query}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 3:
            return None

        return ShowMoreResultsButtonData(
            query_hash=data_split_lst[1],
            query=data_split_lst[2].strip(),
        )


class ShowMoreResultsInlineButton(InlineButton):
    __type__ = InlineButtonType.SHOW_MORE_RESULTS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "more"

    __valid_inline_items__ = [InlineItemType.AUDIO]

    s_more_results = _trans("More results")
    text = f"{s_more_results} | {emoji._plus}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        query_hash: str,
        query: str,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=ShowMoreResultsButtonData.generate_data(query_hash, query),
            lang_code=lang_code,
        )

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        inline_button_data: Optional[ShowMoreResultsButtonData] = None,
    ):
        from tase.telegram.bots.ui.inline_buttons.common import get_query_hash

        query_date = get_now_timestamp()
        from_user = await handler.db.graph.get_interacted_user(telegram_inline_query.from_user)

        # remove the command section from the original query to be like a normal inline query.
        telegram_inline_query.query = inline_button_data.query
        res = CustomInlineQueryResult(telegram_inline_query)

        if inline_button_data.query_hash:
            real_query_hash = get_query_hash(inline_button_data.query)

            if res.is_first_page() and inline_button_data.query_hash == real_query_hash:
                # if this is the first time this query is made, then the first 10 results should be skipped since it is already shown in the non-inline search
                # results.
                res.from_ = 10
            else:
                if inline_button_data.query_hash != real_query_hash:
                    # query hash is invalid, user have changed the original query.
                    pass

            # remove the query hash section from the query string.
            telegram_inline_query.query = inline_button_data.query

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
        inline_button_data: ShowMoreResultsButtonData,
        inline_item_info: AudioItemInfo,
    ):
        # Since the items sent to user are download URLs which is handled by `download_handler`, there is no need for it anymore.
        pass
