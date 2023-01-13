import asyncio
from typing import Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InlineQueryType, ChatType, AudioInteractionType, PlaylistInteractionType
from tase.errors import UserDoesNotHasPlaylist
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData, AudioLinkData
from ..inline_items.item_info import PlaylistItemInfo, AudioItemInfo


class GetPlaylistAudiosButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.GET_PLAYLIST_AUDIOS

    playlist_key: str

    @classmethod
    def generate_data(cls, playlist_key: str) -> Optional[str]:
        return f"${cls.get_type_value()}|{playlist_key}"

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
        inline_button_data: Optional[GetPlaylistAudiosButtonData] = None,
    ):
        playlist_is_valid = False  # whether the requested playlist belongs to the user or not
        audio_vertices = None
        hit_download_urls = None

        playlist = await handler.db.graph.get_playlist_by_key(inline_button_data.playlist_key)

        if result.is_first_page():
            from tase.telegram.bots.ui.inline_items import PlaylistItem

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
                    inline_button_data.playlist_key,
                    offset=result.from_,
                )
            except UserDoesNotHasPlaylist:
                # since it is already been checked that the playlist belongs to the user, this exception will not occur
                pass
            else:
                from tase.telegram.bots.ui.inline_items import AudioItem

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
                            InlineQueryType.PUBLIC_PLAYLIST_COMMAND if playlist.is_public else InlineQueryType.PRIVATE_PLAYLIST_COMMAND,
                            AudioLinkData.generate_data(
                                hit_download_url,
                                playlist_key=playlist.key if playlist.is_public else None,
                                inline_button_type=self.__type__,
                            ),
                            playlist_key=playlist.key,
                        )
                        for audio_doc, audio_vertex, hit_download_url, in zip(audio_docs, audio_vertices, hit_download_urls)
                        if audio_doc and audio_vertex and audio_doc.key not in invalid_audio_keys
                    )
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
                inline_query_type=InlineQueryType.PUBLIC_PLAYLIST_COMMAND if playlist.is_public else InlineQueryType.PRIVATE_PLAYLIST_COMMAND,
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
        if inline_item_info.type == InlineItemType.AUDIO:
            if inline_item_info.valid_for_inline:
                # update the keyboard markup of the downloaded audio
                await handler.update_audio_keyboard_markup(
                    client,
                    from_user,
                    telegram_chosen_inline_result,
                    inline_item_info.hit_download_url,
                    inline_item_info.chat_type,
                    inline_button_type=self.__type__,
                    playlist_key=inline_item_info.playlist_key,
                )
            else:
                await handler.on_inline_audio_article_item_clicked(
                    from_user,
                    client,
                    inline_item_info.chat_type,
                    inline_item_info.hit_download_url,
                    AudioLinkData.generate_data(
                        inline_item_info.hit_download_url,
                        inline_item_info.playlist_key,
                        inline_button_type=self.__type__,
                    ),
                    playlist_key=inline_item_info.playlist_key,
                    inline_button_type=self.__type__,
                )

            playlist = await handler.db.graph.get_playlist_by_key(inline_item_info.playlist_key)
            if not playlist:
                return

            if inline_item_info.inline_query_type == InlineQueryType.PRIVATE_PLAYLIST_COMMAND:
                audio_int_type = AudioInteractionType.REDOWNLOAD_AUDIO
                playlist_int_type = PlaylistInteractionType.REDOWNLOAD_AUDIO

            elif inline_item_info.inline_query_type == InlineQueryType.PUBLIC_PLAYLIST_COMMAND:
                if await handler.db.graph.get_audio_interaction_by_user(
                    from_user,
                    inline_item_info.hit_download_url,
                    AudioInteractionType.DOWNLOAD_AUDIO,
                ):
                    if inline_item_info.chat_type == ChatType.BOT:
                        audio_int_type = AudioInteractionType.REDOWNLOAD_AUDIO
                    else:
                        if from_user.user_id == playlist.owner_user_id:
                            if inline_item_info.valid_for_inline:
                                audio_int_type = AudioInteractionType.SHARE_AUDIO
                            else:
                                audio_int_type = AudioInteractionType.SHARE_AUDIO_LINK

                        else:
                            if inline_item_info.valid_for_inline:
                                audio_int_type = AudioInteractionType.REDOWNLOAD_AUDIO
                            else:
                                audio_int_type = AudioInteractionType.SHARE_AUDIO_LINK
                else:
                    if inline_item_info.valid_for_inline:
                        audio_int_type = AudioInteractionType.DOWNLOAD_AUDIO
                    else:
                        audio_int_type = AudioInteractionType.SHARE_AUDIO_LINK

                if await handler.db.graph.get_playlist_audio_interaction_by_user(
                    from_user,
                    inline_item_info.hit_download_url,
                    playlist.key,
                    PlaylistInteractionType.DOWNLOAD_AUDIO,
                ):
                    if inline_item_info.chat_type == ChatType.BOT:
                        playlist_int_type = PlaylistInteractionType.REDOWNLOAD_AUDIO
                    else:
                        if from_user.user_id == playlist.owner_user_id:
                            if inline_item_info.valid_for_inline:
                                playlist_int_type = PlaylistInteractionType.SHARE_AUDIO
                            else:
                                playlist_int_type = PlaylistInteractionType.SHARE_AUDIO_LINK
                        else:
                            if inline_item_info.valid_for_inline:
                                playlist_int_type = PlaylistInteractionType.REDOWNLOAD_AUDIO
                            else:
                                playlist_int_type = PlaylistInteractionType.SHARE_AUDIO_LINK
                else:
                    if inline_item_info.valid_for_inline:
                        playlist_int_type = PlaylistInteractionType.DOWNLOAD_AUDIO
                    else:
                        playlist_int_type = PlaylistInteractionType.SHARE_AUDIO_LINK
            else:
                return

            if not await handler.db.graph.create_audio_interaction(
                from_user,
                handler.telegram_client.telegram_id,
                audio_int_type,
                inline_item_info.chat_type,
                inline_item_info.hit_download_url,
            ):
                # could not create the interaction_vertex
                logger.error("Could not create the `interaction_vertex` vertex:")
                logger.error(telegram_chosen_inline_result)

            if not await handler.db.graph.create_playlist_interaction(
                from_user,
                handler.telegram_client.telegram_id,
                playlist_int_type,
                inline_item_info.chat_type,
                inline_item_info.playlist_key,
                audio_hit_download_url=inline_item_info.hit_download_url,
            ):
                # could not create the interaction_vertex
                logger.error("Could not create the `interaction_vertex` vertex:")
                logger.error(telegram_chosen_inline_result)

        elif inline_item_info.type == InlineItemType.PLAYLIST:
            from tase.telegram.bots.ui.inline_buttons.common import update_playlist_keyboard_markup

            await update_playlist_keyboard_markup(
                handler.db,
                client,
                from_user,
                telegram_chosen_inline_result,
                inline_item_info,
            )
