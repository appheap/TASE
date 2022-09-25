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
        inline_query_id = result_id_list[0]
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
                    reply_markup.inline_keyboard[1][
                        0
                    ].text = f"{emoji._dark_thumbs_down if not has_disliked else emoji._light_thumbs_down}"

                    if update_like_button:
                        reply_markup.inline_keyboard[1][
                            1
                        ].text = f"{emoji._dark_thumbs_up if not is_liked else emoji._light_thumbs_up}"
                    try:
                        telegram_callback_query.edit_message_reply_markup(reply_markup)
                    except Exception as e:
                        pass
            else:
                telegram_callback_query.answer("Internal error")

    def change_text(
        self,
        has_liked: bool,
    ) -> ToggleDisLikeAudioInlineButton:
        self.text = (
            f"{emoji._dark_thumbs_down if has_liked else emoji._light_thumbs_down}"
        )
        return self
