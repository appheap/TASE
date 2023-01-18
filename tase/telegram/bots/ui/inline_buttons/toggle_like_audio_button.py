from __future__ import annotations

from typing import Optional, List

import pyrogram

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType, AudioInteractionType, PlaylistInteractionType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.errors import (
    UserDoesNotHasPlaylist,
    HitDoesNotExists,
    HitNoLinkedAudio,
)
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData


class ToggleLikeAudioButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.LIKE_AUDIO

    chat_type: ChatType
    hit_download_url: str
    playlist_key: Optional[str]

    @classmethod
    def generate_data(
        cls,
        chat_type: ChatType,
        hit_download_url: str,
        playlist_key: Optional[str] = None,
    ) -> Optional[str]:
        s_ = f"{cls.get_type_value()}|{chat_type.value}|{hit_download_url}"
        if playlist_key:
            return s_ + f"|{playlist_key}"

        return s_

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) < 3:
            return None

        return ToggleLikeAudioButtonData(
            chat_type=ChatType(int(data_split_lst[1])),
            hit_download_url=data_split_lst[2],
            playlist_key=data_split_lst[3] if len(data_split_lst) > 3 else None,
        )


class ToggleLikeAudioInlineButton(InlineButton):
    __type__ = InlineButtonType.LIKE_AUDIO
    action = ButtonActionType.CALLBACK

    text = f"{emoji._light_thumbs_up}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        chat_type: ChatType,
        hit_download_url: str,
        lang_code: Optional[str] = "en",
        playlist_key: Optional[str] = None,
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=ToggleLikeAudioButtonData.generate_data(
                chat_type,
                hit_download_url,
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
        inline_button_data: ToggleLikeAudioButtonData,
    ):
        hit_download_url = inline_button_data.hit_download_url
        chat_type = inline_button_data.chat_type

        try:
            successful, has_liked = await handler.db.graph.toggle_audio_interaction(
                from_user,
                handler.telegram_client.telegram_id,
                hit_download_url,
                chat_type,
                AudioInteractionType.LIKE_AUDIO,
            )

            if inline_button_data.playlist_key:
                if not successful:
                    is_liked = await handler.db.graph.audio_is_interacted_by_user(
                        from_user,
                        AudioInteractionType.LIKE_AUDIO,
                        hit_download_url=hit_download_url,
                    )
                else:
                    is_liked = None

                await handler.db.graph.toggle_playlist_interaction(
                    from_user,
                    handler.telegram_client.telegram_id,
                    chat_type,
                    PlaylistInteractionType.LIKE_AUDIO,
                    inline_button_data.playlist_key,
                    is_active=not has_liked if successful else is_liked,
                    audio_hit_download_url=inline_button_data.hit_download_url,
                    create_if_not_exists=False,
                )

        except UserDoesNotHasPlaylist as e:
            await telegram_callback_query.answer("You do not have the playlist you have chosen")
        except HitDoesNotExists as e:
            await telegram_callback_query.answer("Given download url is not valid anymore")
        except HitNoLinkedAudio as e:
            await telegram_callback_query.answer("Audio does not exist anymore")
        except Exception as e:
            logger.exception(e)
            await telegram_callback_query.answer("Could not add the audio to the playlist due to internal error")
        else:
            # todo: update these messages
            if successful:
                is_disliked = await handler.db.graph.audio_is_interacted_by_user(
                    from_user,
                    AudioInteractionType.DISLIKE_AUDIO,
                    hit_download_url=hit_download_url,
                )
                update_dislike_button = False
                if not has_liked and is_disliked:
                    successful, has_disliked = await handler.db.graph.toggle_audio_interaction(
                        from_user,
                        handler.telegram_client.telegram_id,
                        hit_download_url,
                        chat_type,
                        AudioInteractionType.DISLIKE_AUDIO,
                    )

                    if inline_button_data.playlist_key:
                        await handler.db.graph.toggle_playlist_interaction(
                            from_user,
                            handler.telegram_client.telegram_id,
                            chat_type,
                            PlaylistInteractionType.DISLIKE_AUDIO,
                            inline_button_data.playlist_key,
                            is_active=not has_disliked if successful else is_disliked,
                            audio_hit_download_url=inline_button_data.hit_download_url,
                            create_if_not_exists=False,
                        )

                    update_dislike_button = True

                await telegram_callback_query.answer(f"You {'Unliked' if has_liked else 'Liked'} this song")

                if telegram_callback_query.message is not None:
                    reply_markup = telegram_callback_query.message.reply_markup
                    like_dislike_index = 1 if len(reply_markup.inline_keyboard) == 3 else 0
                    reply_markup.inline_keyboard[like_dislike_index][1].text = self.new_text(not has_liked)

                    if update_dislike_button:
                        reply_markup.inline_keyboard[like_dislike_index][0].text = self.new_text(
                            not is_disliked,
                            thumbs_up=False,
                        )
                    try:
                        await telegram_callback_query.edit_message_reply_markup(reply_markup)
                    except Exception as e:
                        pass
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
                        playlist_key=inline_button_data.playlist_key,
                    )
                    if reply_markup:
                        like_dislike_index = 1 if len(reply_markup.inline_keyboard) == 3 else 0
                        reply_markup.inline_keyboard[like_dislike_index][1].text = self.new_text(not has_liked)

                        if update_dislike_button:
                            reply_markup.inline_keyboard[like_dislike_index][0].text = self.new_text(
                                not is_disliked,
                                thumbs_up=False,
                            )

                        try:
                            await client.edit_inline_reply_markup(
                                telegram_callback_query.inline_message_id,
                                reply_markup,
                            )
                        except Exception as e:
                            logger.exception(e)
            else:
                await telegram_callback_query.answer("Internal error")

    def new_text(
        self,
        active: bool,
        thumbs_up: bool = True,
    ) -> str:
        if thumbs_up:
            return f"{emoji._dark_thumbs_up if active else emoji._light_thumbs_up}"
        else:
            return f"{emoji._dark_thumbs_down if active else emoji._light_thumbs_down}"

    def change_text(
        self,
        is_disliked: bool,
    ) -> ToggleLikeAudioInlineButton:
        self.text = self.new_text(is_disliked)
        return self
