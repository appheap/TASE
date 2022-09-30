from __future__ import annotations

import pyrogram

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType, InteractionType
from tase.errors import (
    PlaylistDoesNotExists,
    HitDoesNotExists,
    HitNoLinkedAudio,
    InvalidAudioForInlineMode,
)
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType


class ToggleLikeAudioInlineButton(InlineButton):
    name = "like_audio"
    type = InlineButtonType.LIKE_AUDIO

    text = f"{emoji._light_thumbs_up}"
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
            successful, has_liked = handler.db.graph.toggle_interaction(
                from_user,
                handler.telegram_client.telegram_id,
                hit_download_url,
                chat_type,
                InteractionType.LIKE,
            )
        except PlaylistDoesNotExists as e:
            telegram_callback_query.answer(
                "You do not have the playlist you have chosen"
            )
        except HitDoesNotExists as e:
            telegram_callback_query.answer("Given download url is not valid anymore")
        except HitNoLinkedAudio as e:
            telegram_callback_query.answer("Audio does not exist anymore")
        except InvalidAudioForInlineMode as e:
            telegram_callback_query.answer("This audio cannot be used in inline mode")
        except Exception as e:
            logger.exception(e)
            telegram_callback_query.answer(
                "Could not add the audio to the playlist due to internal error"
            )
        else:
            # todo: update these messages
            if successful:
                is_disliked = handler.db.graph.audio_is_interacted_by_user(
                    from_user,
                    hit_download_url,
                    InteractionType.DISLIKE,
                )
                update_dislike_button = False
                if not has_liked and is_disliked:
                    handler.db.graph.toggle_interaction(
                        from_user,
                        handler.telegram_client.telegram_id,
                        hit_download_url,
                        chat_type,
                        InteractionType.DISLIKE,
                    )
                    update_dislike_button = True

                telegram_callback_query.answer(
                    f"You {'Unliked' if has_liked else 'Liked'} this song"
                )

                if telegram_callback_query.message is not None:
                    reply_markup = telegram_callback_query.message.reply_markup
                    like_dislike_index = (
                        1 if len(reply_markup.inline_keyboard) == 3 else 0
                    )
                    reply_markup.inline_keyboard[like_dislike_index][
                        1
                    ].text = f"{emoji._dark_thumbs_up if not has_liked else emoji._light_thumbs_up}"

                    if update_dislike_button:
                        reply_markup.inline_keyboard[like_dislike_index][
                            0
                        ].text = f"{emoji._dark_thumbs_down if not is_disliked else emoji._light_thumbs_down}"
                    try:
                        telegram_callback_query.edit_message_reply_markup(reply_markup)
                    except Exception as e:
                        pass
            else:
                telegram_callback_query.answer("Internal error")

    def change_text(
        self,
        has_liked: bool,
    ) -> ToggleLikeAudioInlineButton:
        self.text = f"{emoji._dark_thumbs_up if has_liked else emoji._light_thumbs_up}"
        return self
