from __future__ import annotations

import copy

import pyrogram

from tase.common.utils import emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.errors import (
    PlaylistDoesNotExists,
    HitDoesNotExists,
    HitNoLinkedAudio,
    InvalidAudioForInlineMode,
)
from tase.my_logger import logger
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType


class ToggleFavoritePlaylistInlineButton(InlineButton):
    name = "add_to_fav_playlist"
    type = InlineButtonType.ADD_TO_FAVORITE_PLAYLIST

    text = f"{emoji._red_heart}"
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

        # add the audio to the playlist
        try:
            (
                successful,
                created,
            ), in_favorite_playlist = handler.db.graph.toggle_favorite_playlist(
                from_user,
                hit_download_url,
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
                if created:
                    telegram_callback_query.answer(
                        f"{'Removed from' if in_favorite_playlist else 'Added to'} the favorite playlist"
                    )
                    if telegram_callback_query.message is not None:
                        reply_markup = telegram_callback_query.message.reply_markup
                        reply_markup.inline_keyboard[0][
                            2
                        ].text = f"{emoji._red_heart if not in_favorite_playlist else emoji._white_heart}"
                        telegram_callback_query.edit_message_reply_markup(reply_markup)
                else:
                    telegram_callback_query.answer("It's already on the playlist")
            else:
                telegram_callback_query.answer(
                    "Did not add to / remove from the playlist"
                )

    def change_text(
        self,
        in_favorite_playlist: bool,
    ) -> ToggleFavoritePlaylistInlineButton:
        self.text = (
            f"{emoji._red_heart if in_favorite_playlist else emoji._white_heart}"
        )
        return self
