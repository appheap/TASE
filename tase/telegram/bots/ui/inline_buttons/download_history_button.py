from __future__ import annotations

import asyncio
from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InlineQueryType, ChatType, AudioInteractionType
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData
from ..inline_items.item_info import AudioItemInfo


class DownloadHistoryButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.DOWNLOAD_HISTORY

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"${inline_command}"

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
    __switch_inline_query_aliases__ = [
        "dl",
        "dls",
        "download",
    ]

    __valid_inline_items__ = [InlineItemType.AUDIO]

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
            only_include_valid_audios_for_inline_search=False,
        )

        hit_download_urls = None
        if audio_vertices:
            from tase.telegram.bots.ui.inline_items import AudioItem
            from tase.telegram.bots.ui.base import DownloadHistoryAudioLinkData

            # todo: fix this
            chats_dict, invalid_audio_keys = await handler.update_audio_cache(audio_vertices)

            audio_docs = await asyncio.gather(
                *(
                    handler.db.document.get_audio_by_key(
                        audio_vertex.get_doc_cache_key(handler.telegram_client.telegram_id),
                    )
                    for audio_vertex in audio_vertices
                )
            )
            hit_download_urls = await handler.db.graph.generate_hit_download_urls(size=len(audio_vertices))

            username = (await handler.telegram_client.get_me()).username

            result.extend_results(
                (
                    AudioItem.get_item(
                        username,
                        audio_doc.file_id,
                        from_user,
                        audio_vertex,
                        telegram_inline_query,
                        chats_dict,
                        hit_download_url,
                        InlineQueryType.AUDIO_COMMAND,
                        DownloadHistoryAudioLinkData.generate_data(hit_download_url),
                    )
                    for audio_doc, audio_vertex, hit_download_url, in zip(audio_docs, audio_vertices, hit_download_urls)
                    if audio_doc and audio_vertex and audio_doc.key not in invalid_audio_keys
                )
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
            inline_query_type=InlineQueryType.AUDIO_COMMAND,
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
        inline_item_info: AudioItemInfo,
    ):
        from tase.telegram.bots.ui.base import DownloadHistoryAudioLinkData

        if inline_item_info.type != InlineItemType.AUDIO:
            logger.error(f"ChosenInlineResult `{telegram_chosen_inline_result.result_id}` is not valid.")
            return

        if inline_item_info.inline_query_type == InlineQueryType.AUDIO_COMMAND:
            if inline_item_info.valid_for_inline:
                if inline_item_info.chat_type == ChatType.BOT:
                    type_ = AudioInteractionType.REDOWNLOAD_AUDIO
                else:
                    type_ = AudioInteractionType.SHARE_AUDIO
            else:
                if inline_item_info.chat_type == ChatType.BOT:
                    type_ = AudioInteractionType.REDOWNLOAD_AUDIO
                else:
                    type_ = AudioInteractionType.SHARE_AUDIO_LINK
        else:
            return

        if not await handler.db.graph.create_audio_interaction(
            from_user,
            handler.telegram_client.telegram_id,
            type_,
            inline_item_info.chat_type,
            inline_item_info.hit_download_url,
        ):
            # could not create the download
            logger.error("Could not create the `interaction_vertex` vertex:")
            logger.error(telegram_chosen_inline_result)

        if inline_item_info.valid_for_inline:
            # update the keyboard markup of the downloaded audio
            await handler.update_audio_keyboard_markup(
                client,
                from_user,
                telegram_chosen_inline_result,
                inline_item_info.hit_download_url,
                inline_item_info.chat_type,
                self.__type__,
            )

        else:
            await handler.on_inline_audio_article_item_clicked(
                from_user,
                client,
                inline_item_info.chat_type,
                inline_item_info.hit_download_url,
                DownloadHistoryAudioLinkData.generate_data(inline_item_info.hit_download_url),
                self.__type__,
            )
