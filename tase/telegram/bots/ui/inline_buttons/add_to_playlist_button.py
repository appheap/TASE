from typing import Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType, AudioInteractionType
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
from ..inline_items.item_info import CreateNewPublicPlaylistItemInfo, CreateNewPrivatePlaylistItemInfo, PlaylistItemInfo


class AddToPlaylistButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.ADD_TO_PLAYLIST

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

        return AddToPlaylistButtonData(
            audio_hit_download_url=data_split_lst[1],
            playlist_key=data_split_lst[2] if len(data_split_lst) > 2 else None,
        )


class AddToPlaylistInlineButton(InlineButton):
    __type__ = InlineButtonType.ADD_TO_PLAYLIST
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "add_to_pl"

    __valid_inline_items__ = [
        InlineItemType.PLAYLIST,
        InlineItemType.CREATE_NEW_PUBLIC_PLAYLIST,
        InlineItemType.CREATE_NEW_PRIVATE_PLAYLIST,
    ]

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{emoji._plus}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        audio_hit_download_url: str,
        playlist_key: Optional[str] = None,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return InlineButton.get_button(cls.__type__).__parse_keyboard_button__(
            lang_code=lang_code,
            switch_inline_query_current_chat=AddToPlaylistButtonData.generate_data(
                audio_hit_download_url=audio_hit_download_url,
                playlist_key=playlist_key,
            ),
        )

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        inline_button_data: Optional[AddToPlaylistButtonData] = None,
    ):
        from tase.telegram.bots.ui.inline_buttons.common import populate_playlist_list

        await populate_playlist_list(
            from_user,
            handler,
            result,
            telegram_inline_query,
            filter_by_capacity=True,
            view_playlist=False,
        )

        await result.answer_query()

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: AddToPlaylistButtonData,
        inline_item_info: Union[CreateNewPublicPlaylistItemInfo, CreateNewPrivatePlaylistItemInfo, PlaylistItemInfo],
    ):
        # todo: check if the user has downloaded this audio earlier, otherwise, the request is not valid

        playlist_key = inline_item_info.playlist_key if inline_item_info.type == InlineItemType.PLAYLIST else inline_item_info.item_key

        if playlist_key in ("add_a_new_private_playlist", "add_a_new_public_playlist"):
            # start creating a new playlist
            await handler.db.document.create_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PRIVATE_PLAYLIST if playlist_key == "add_a_new_private_playlist" else BotTaskType.CREATE_NEW_PUBLIC_PLAYLIST,
                state_dict={
                    "hit_download_url": inline_button_data.audio_hit_download_url,
                },
            )

            await client.send_message(
                from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line\nYou can cancel anytime by sending /cancel",
            )
        else:
            # add the audio to the playlist
            try:
                successful, created = await handler.db.graph.add_audio_to_playlist(
                    from_user,
                    playlist_key,
                    inline_button_data.audio_hit_download_url,
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
                    "Could not add the audio to the playlist due to internal error",
                )
            else:
                # todo: update these messages
                if successful:
                    if created:
                        await client.send_message(
                            from_user.user_id,
                            "Added to the playlist",
                        )
                        chosen_playlist = await handler.db.graph.get_user_playlist_by_key(from_user, playlist_key)
                        if chosen_playlist:
                            await chosen_playlist.update_last_modified_date()

                            await handler.db.graph.toggle_audio_interaction(
                                from_user,
                                handler.telegram_client.telegram_id,
                                inline_button_data.audio_hit_download_url,
                                inline_item_info.chat_type,
                                AudioInteractionType.ADD_TO_PUBLIC_PLAYLIST if chosen_playlist.is_public else AudioInteractionType.ADD_TO_PRIVATE_PLAYLIST,
                                playlist_key=playlist_key,
                                is_active=True,
                            )

                    else:
                        await client.send_message(
                            from_user.user_id,
                            "It's already on the playlist",
                        )
                else:
                    await client.send_message(
                        from_user.user_id,
                        "Did not add to the playlist",
                    )
