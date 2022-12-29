import asyncio
from typing import Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InteractionType, InlineQueryType
from tase.errors import PlaylistDoesNotExists
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData
from ..inline_items.item_info import PlaylistItemInfo, AudioItemInfo


class GetPlaylistAudiosButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.GET_PLAYLIST_AUDIOS

    playlist_key: str

    @classmethod
    def generate_data(cls, playlist_key: str) -> Optional[str]:
        return f"#{cls.get_type_value()}|{playlist_key}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 2:
            return None

        return GetPlaylistAudiosButtonData(playlist_key=data_split_lst[1])


class GetPlaylistAudioInlineButton(InlineButton):
    __type__ = InlineButtonType.GET_PLAYLIST_AUDIOS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "get_pl"

    __valid_inline_items__ = [
        InlineItemType.AUDIO,
        InlineItemType.PLAYLIST,
    ]

    s_audios = _trans("Audio Files")
    text = f"{s_audios} | {emoji._headphone}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        playlist_key: str,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=GetPlaylistAudiosButtonData.generate_data(playlist_key),
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
        inline_button_data: Optional[InlineButtonData] = None,
    ):
        inline_button_data: GetPlaylistAudiosButtonData = inline_button_data
        playlist_key = inline_button_data.playlist_key

        playlist_is_valid = False  # whether the requested playlist belongs to the user or not
        audio_vertices = None
        hit_download_urls = None

        if result.is_first_page():
            from tase.telegram.bots.ui.inline_items import PlaylistItem

            playlist = await handler.db.graph.get_playlist_by_key(playlist_key)

            if playlist and not playlist.is_soft_deleted:
                if not playlist.is_public:
                    # if this playlist is private, then it can only be accessed if the user querying it is the owner.
                    if playlist.owner_user_id == from_user.user_id:
                        playlist_is_valid = True
                        result.add_item(
                            PlaylistItem.get_item(
                                playlist,
                                from_user,
                                telegram_inline_query,
                                view_playlist=True,
                            ),
                            count=False,
                        )
                else:
                    playlist_is_valid = True
                    result.add_item(
                        PlaylistItem.get_item(
                            playlist,
                            from_user,
                            telegram_inline_query,
                            view_playlist=True,
                        ),
                        count=False,
                    )
        else:
            # since the playlist validation has been done in the first page, it is not necessary to redo it.
            playlist_is_valid = True

        if playlist_is_valid:
            try:
                audio_vertices = await handler.db.graph.get_playlist_audios(
                    playlist_key,
                    offset=result.from_,
                )
            except PlaylistDoesNotExists:
                # since it is already been checked that the playlist belongs to the user, this exception will not occur
                pass
            else:
                from tase.telegram.bots.ui.inline_buttons.common import populate_audio_items

                hit_download_urls = await populate_audio_items(
                    audio_vertices,
                    from_user,
                    handler,
                    result,
                    telegram_inline_query,
                )

        if not len(result) and not playlist_is_valid and result.is_first_page():
            from tase.telegram.bots.ui.inline_items import NoDownloadItem

            result.set_results([NoDownloadItem.get_item(from_user)])

        await result.answer_query()

        if playlist_is_valid and audio_vertices and hit_download_urls:
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
        inline_button_data: GetPlaylistAudiosButtonData,
        inline_item_info: Union[AudioItemInfo, PlaylistItemInfo],
    ):
        # only if the user has clicked on an audio item, the rest of the code should be executed.
        if inline_item_info.type != InlineItemType.AUDIO:
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
            # could not create the interaction_vertex
            logger.error("Could not create the `interaction_vertex` vertex:")
            logger.error(telegram_chosen_inline_result)

        await update_keyboard_task
