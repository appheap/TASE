from __future__ import annotations

from typing import List, Optional

import pyrogram

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType, AudioInteractionType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.errors import (
    UserDoesNotHasPlaylist,
    HitDoesNotExists,
    HitNoLinkedAudio,
    InvalidAudioForInlineMode,
)
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData


class ToggleFavoritePlaylistButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.ADD_TO_FAVORITE_PLAYLIST

    chat_type: ChatType
    audio_hit_download_url: str
    playlist_key: Optional[str]

    @classmethod
    def generate_data(
        cls,
        chat_type: ChatType,
        audio_hit_download_url: str,
        playlist_key: Optional[str] = None,
    ) -> Optional[str]:
        temp = f"{cls.get_type_value()}|{chat_type.value}|{audio_hit_download_url}"

        if playlist_key:
            return temp + f"|{playlist_key}"

        return temp

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) < 3:
            return None

        return ToggleFavoritePlaylistButtonData(
            chat_type=ChatType(int(data_split_lst[1])),
            audio_hit_download_url=data_split_lst[2],
            playlist_key=data_split_lst[3] if len(data_split_lst) > 3 else None,
        )


class ToggleFavoritePlaylistInlineButton(InlineButton):
    __type__ = InlineButtonType.ADD_TO_FAVORITE_PLAYLIST
    action = ButtonActionType.CALLBACK

    text = f"{emoji._red_heart}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        chat_type: ChatType,
        audio_hit_download_url: str,
        playlist_key: Optional[str] = None,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=ToggleFavoritePlaylistButtonData.generate_data(
                chat_type=chat_type,
                audio_hit_download_url=audio_hit_download_url,
                playlist_key=playlist_key,
            ),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: ToggleFavoritePlaylistButtonData,
    ):
        hit_download_url = inline_button_data.audio_hit_download_url
        chat_type = inline_button_data.chat_type

        # add the audio to the playlist
        try:
            (successful, created), in_favorite_playlist = await handler.db.graph.toggle_favorite_playlist(
                from_user,
                hit_download_url,
            )
        except UserDoesNotHasPlaylist as e:
            await telegram_callback_query.answer("You do not have the playlist you have chosen")
        except HitDoesNotExists as e:
            await telegram_callback_query.answer("Given download url is not valid anymore")
        except HitNoLinkedAudio as e:
            await telegram_callback_query.answer("Audio does not exist anymore")
        except InvalidAudioForInlineMode as e:
            await telegram_callback_query.answer("This audio cannot be used in inline mode")
        except Exception as e:
            logger.exception(e)
            await telegram_callback_query.answer("Could not add the audio to the playlist due to internal error")
        else:
            # todo: update these messages
            if successful:
                if created:
                    await telegram_callback_query.answer(f"{'Removed from' if in_favorite_playlist else 'Added to'} the favorite playlist")
                    if telegram_callback_query.message is not None:
                        reply_markup = telegram_callback_query.message.reply_markup
                        reply_markup.inline_keyboard[0][2].text = self.new_text(not in_favorite_playlist)

                        await telegram_callback_query.edit_message_reply_markup(reply_markup)
                    elif telegram_callback_query.inline_message_id:
                        status = await AudioKeyboardStatus.get_status(
                            handler.db,
                            from_user,
                            hit_download_url=hit_download_url,
                        )
                        from tase.telegram.bots.ui.inline_buttons.common import get_audio_markup_keyboard

                        reply_markup = get_audio_markup_keyboard(
                            (await handler.telegram_client.get_me()).username,
                            chat_type,
                            from_user.chosen_language_code,
                            hit_download_url,
                            status,
                        )
                        if reply_markup:
                            reply_markup.inline_keyboard[0][2].text = self.new_text(not in_favorite_playlist)
                            try:
                                await client.edit_inline_reply_markup(
                                    telegram_callback_query.inline_message_id,
                                    reply_markup,
                                )
                            except Exception as e:
                                logger.exception(e)

                    fav_playlist = await handler.db.graph.get_user_favorite_playlist(from_user)
                    if fav_playlist:
                        await handler.db.graph.toggle_audio_interaction(
                            from_user,
                            handler.telegram_client.telegram_id,
                            inline_button_data.audio_hit_download_url,
                            inline_button_data.chat_type,
                            AudioInteractionType.ADD_TO_FAVORITE_PLAYLIST,
                            playlist_key=fav_playlist.key,
                            create_if_not_exists=True if not in_favorite_playlist else False,
                            is_active=not in_favorite_playlist,
                        )
                else:
                    await telegram_callback_query.answer("It's already on the playlist")
            else:
                await telegram_callback_query.answer("Did not add to / remove from the playlist")

    def new_text(
        self,
        active: bool,
    ) -> str:
        return f"{emoji._red_heart if active else emoji._white_heart}"

    def change_text(
        self,
        active: bool,
    ) -> ToggleFavoritePlaylistInlineButton:
        self.text = self.new_text(active)
        return self
