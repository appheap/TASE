from __future__ import annotations

import pyrogram

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType, InteractionType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.errors import (
    PlaylistDoesNotExists,
    HitDoesNotExists,
    HitNoLinkedAudio,
)
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType
from .common import get_audio_markup_keyboard


class ToggleDisLikeAudioInlineButton(InlineButton):
    name = "dislike_audio"
    type = InlineButtonType.DISLIKE_AUDIO

    text = f"{emoji._light_thumbs_down}"
    is_inline = False

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        result_id_list = telegram_callback_query.data.split("->")
        button_type_value = result_id_list[0]
        hit_download_url = result_id_list[1]
        chat_type = ChatType(int(result_id_list[2]))

        try:
            successful, has_disliked = handler.db.graph.toggle_interaction(
                from_user,
                handler.telegram_client.telegram_id,
                hit_download_url,
                chat_type,
                InteractionType.DISLIKE,
            )
        except PlaylistDoesNotExists as e:
            telegram_callback_query.answer(
                "You do not have the playlist you have chosen"
            )
        except HitDoesNotExists as e:
            telegram_callback_query.answer("Given download url is not valid anymore")
        except HitNoLinkedAudio as e:
            telegram_callback_query.answer("Audio does not exist anymore")
        except Exception as e:
            logger.exception(e)
            telegram_callback_query.answer(
                "Could not add the audio to the playlist due to internal error"
            )
        else:
            # todo: update these messages
            if successful:
                is_liked = handler.db.graph.audio_is_interacted_by_user(
                    from_user,
                    hit_download_url,
                    InteractionType.LIKE,
                )
                update_like_button = False
                if not has_disliked and is_liked:
                    handler.db.graph.toggle_interaction(
                        from_user,
                        handler.telegram_client.telegram_id,
                        hit_download_url,
                        chat_type,
                        InteractionType.LIKE,
                    )
                    update_like_button = True

                telegram_callback_query.answer(
                    f"You {'Un-disliked' if has_disliked else 'Disliked'} this song"
                )

                if telegram_callback_query.message is not None:
                    reply_markup = telegram_callback_query.message.reply_markup
                    like_dislike_index = (
                        1 if len(reply_markup.inline_keyboard) == 3 else 0
                    )
                    reply_markup.inline_keyboard[like_dislike_index][
                        0
                    ].text = self.new_text(not has_disliked)

                    if update_like_button:
                        reply_markup.inline_keyboard[like_dislike_index][
                            1
                        ].text = self.new_text(
                            not is_liked,
                            thumbs_down=False,
                        )
                    try:
                        telegram_callback_query.edit_message_reply_markup(reply_markup)
                    except Exception as e:
                        pass
                elif telegram_callback_query.inline_message_id:
                    audio_inline_message = handler.db.document.find_audio_inline_message_by_message_inline_id(
                        handler.telegram_client.telegram_id,
                        from_user.user_id,
                        telegram_callback_query.inline_message_id,
                    )
                    if audio_inline_message:
                        status = AudioKeyboardStatus.get_status(
                            handler.db,
                            from_user,
                            hit_download_url,
                        )
                        reply_markup = get_audio_markup_keyboard(
                            handler.telegram_client.get_me().username,
                            chat_type,
                            from_user.chosen_language_code,
                            hit_download_url,
                            True,
                            status,
                        )
                        if reply_markup:
                            like_dislike_index = (
                                1 if len(reply_markup.inline_keyboard) == 3 else 0
                            )
                            reply_markup.inline_keyboard[like_dislike_index][
                                0
                            ].text = self.new_text(not has_disliked)

                            if update_like_button:
                                reply_markup.inline_keyboard[like_dislike_index][
                                    1
                                ].text = self.new_text(
                                    not is_liked,
                                    thumbs_down=False,
                                )

                            try:
                                client.edit_inline_reply_markup(
                                    telegram_callback_query.inline_message_id,
                                    reply_markup,
                                )
                            except Exception as e:
                                logger.exception(e)
            else:
                telegram_callback_query.answer("Internal error")

    def new_text(
        self,
        active: bool,
        thumbs_down: bool = True,
    ) -> str:
        if thumbs_down:
            return f"{emoji._dark_thumbs_down if active else emoji._light_thumbs_down}"
        else:
            return f"{emoji._dark_thumbs_up if active else emoji._light_thumbs_up}"

    def change_text(
        self,
        active: bool,
    ) -> ToggleDisLikeAudioInlineButton:
        self.text = self.new_text(active)
        return self
