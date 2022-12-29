import asyncio
from typing import Match, Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InteractionType, InlineQueryType
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemInfo, InlineItemType, InlineButtonData


class DownloadHistoryButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.DOWNLOAD_HISTORY

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"#{inline_command}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return DownloadHistoryButtonData()


class DownloadHistoryInlineButton(InlineButton):
    __type__ = InlineButtonType.DOWNLOAD_HISTORY
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "downloads"

    s_my_downloads = _trans("My Downloads")
    text = f"{s_my_downloads} | {emoji._mobile_phone_with_arrow}"

    @classmethod
    def get_keyboard(
        cls,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=DownloadHistoryButtonData.generate_data(cls.switch_inline_query()),
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
        inline_button_data: Optional[DownloadHistoryButtonData] = None,
    ):
        audio_vertices = await handler.db.graph.get_user_download_history(
            from_user,
            offset=result.from_,
        )

        from tase.telegram.bots.ui.inline_buttons.common import populate_audio_items

        hit_download_urls = await populate_audio_items(
            audio_vertices,
            from_user,
            handler,
            result,
            telegram_inline_query,
        )

        if not len(result) and result.is_first_page():
            from tase.telegram.bots.ui.inline_items import NoDownloadItem

            result.set_results([NoDownloadItem.get_item(from_user)])

        await result.answer_query()

        await handler.db.graph.get_or_create_query(
            handler.telegram_client.telegram_id,
            from_user,
            telegram_inline_query.query,
            query_date,
            audio_vertices,
            telegram_inline_query=telegram_inline_query,
            inline_query_type=InlineQueryType.COMMAND,
            next_offset=result.get_next_offset(only_countable=True),
            hit_download_urls=hit_download_urls,
        )

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: DownloadHistoryButtonData,
    ):

        from tase.telegram.bots.ui.inline_items.item_info import AudioItemInfo

        inline_item_info: Optional[AudioItemInfo] = InlineItemInfo.get_info(telegram_chosen_inline_result.result_id)
        if not inline_item_info or inline_item_info.type != InlineItemType.AUDIO:
            logger.error(f"ChosenInlineResult `{telegram_chosen_inline_result.result_id}` is not valid.")
            return

        # update the keyboard markup of the downloaded audio
        update_keyboard_task = asyncio.create_task(
            handler.update_audio_keyboard_markup(
                client,
                from_user,
                telegram_chosen_inline_result,
                inline_item_info.hit_download_url,
                inline_item_info.chat_type,
            )
        )

        interaction_vertex = await handler.db.graph.create_interaction(
            inline_item_info.hit_download_url,
            from_user,
            handler.telegram_client.telegram_id,
            InteractionType.SHARE,
            inline_item_info.chat_type,
        )
        if not interaction_vertex:
            # could not create the download
            logger.error("Could not create the `interaction_vertex` vertex:")
            logger.error(telegram_chosen_inline_result)

        await update_keyboard_task
