from typing import Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import AudioInteractionType
from tase.errors import (
    UserDoesNotHasPlaylist,
    HitDoesNotExists,
    HitNoLinkedAudio,
    InvalidAudioForInlineMode,
)
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData
from ..inline_items.item_info import PlaylistItemInfo, NoPlaylistItemInfo


class RemoveFromPlaylistButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.REMOVE_FROM_PLAYLIST

    audio_hit_download_url: str
    playlist_key: Optional[str]

    @classmethod
    def generate_data(
        cls,
        audio_hit_download_url: str,
        playlist_key: Optional[str] = None,
    ) -> Optional[str]:
        temp = f"${cls.get_type_value()}|{audio_hit_download_url}"

        if playlist_key:
            return temp + f"|{playlist_key}"

        return temp

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) < 2:
            return None

        return RemoveFromPlaylistButtonData(
            audio_hit_download_url=data_split_lst[1],
            playlist_key=data_split_lst[2] if len(data_split_lst) > 2 else None,
        )


class RemoveFromPlaylistInlineButton(InlineButton):
    __type__ = InlineButtonType.REMOVE_FROM_PLAYLIST
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "remove_from_pl"

    __valid_inline_items__ = [
        InlineItemType.PLAYLIST,
        InlineItemType.NO_PLAYLIST,
    ]

    s_remove_from_playlist = _trans("Remove From Playlist")
    text = f"{emoji._minus}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        audio_hit_download_url: str,
        playlist_key: Optional[str] = None,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=RemoveFromPlaylistButtonData.generate_data(
                audio_hit_download_url=audio_hit_download_url,
                playlist_key=playlist_key,
            ),
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
        inline_button_data: Optional[RemoveFromPlaylistButtonData] = None,
    ):
        try:
            db_playlists = await handler.db.graph.get_audio_playlists(
                from_user,
                inline_button_data.audio_hit_download_url,
                offset=result.from_,
            )
        except HitNoLinkedAudio:
            # fixme: this happens if the hit with the given `download_url` does not have any audio vertex linked to
            #  it. notify the user about this situation and update the database
            await client.send_message(
                from_user.user_id,
                "Given download url is not valid anymore",
            )
        else:
            from tase.telegram.bots.ui.inline_items import PlaylistItem

            for playlist in db_playlists:
                result.add_item(
                    PlaylistItem.get_item(
                        playlist,
                        from_user,
                        telegram_inline_query,
                        view_playlist=False,
                    )
                )

        if not len(result) and result.is_first_page():
            # what to show when user doesn't have any playlists yet or hasn't added this audio to any playlist
            from tase.telegram.bots.ui.inline_items import AudioInNoPlaylistItem

            result.set_results([AudioInNoPlaylistItem.get_item(from_user)])

        await result.answer_query()

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: RemoveFromPlaylistButtonData,
        inline_item_info: Union[PlaylistItemInfo, NoPlaylistItemInfo],
    ):
        if inline_item_info.type != InlineItemType.PLAYLIST:
            return

        # todo: check if the user has downloaded this audio earlier, otherwise, the request is not valid

        playlist_key = inline_item_info.playlist_key

        # remove the audio from the playlist
        try:
            successful, removed = await handler.db.graph.remove_audio_from_playlist(
                from_user,
                playlist_key,
                inline_button_data.audio_hit_download_url,
                get_now_timestamp(),
            )
        except UserDoesNotHasPlaylist as e:
            await client.send_message(
                from_user.user_id,
                "You do not have the playlist you have chosen",
            )
        except HitDoesNotExists as e:
            await client.send_message(
                from_user.user_id,
                "Given download url is not valid anymore",
            )
        except HitNoLinkedAudio as e:
            await client.send_message(
                from_user.user_id,
                "Audio does not exist anymore",
            )
        except InvalidAudioForInlineMode as e:
            await client.send_message(
                from_user.user_id,
                "This audio cannot be used in inline mode",
            )
        except Exception as e:
            logger.exception(e)
            await client.send_message(
                from_user.user_id,
                "Could not remove the audio from the playlist",
            )
        else:
            # todo: update these messages
            if successful:
                if removed:
                    await client.send_message(
                        from_user.user_id,
                        "Removed from the playlist",
                    )

                    chosen_playlist = await handler.db.graph.get_user_playlist_by_key(from_user, playlist_key)
                    if chosen_playlist:
                        await handler.db.graph.toggle_audio_interaction(
                            from_user,
                            handler.telegram_client.telegram_id,
                            inline_button_data.audio_hit_download_url,
                            inline_item_info.chat_type,
                            AudioInteractionType.ADD_TO_PUBLIC_PLAYLIST if chosen_playlist.is_public else AudioInteractionType.ADD_TO_PRIVATE_PLAYLIST,
                            playlist_key=playlist_key,
                            create_if_not_exists=False,
                            is_active=False,
                        )

                else:
                    await client.send_message(
                        from_user.user_id,
                        "Did not remove from the playlist",
                    )
            else:
                await client.send_message(
                    from_user.user_id,
                    "Did not remove from the playlist",
                )
