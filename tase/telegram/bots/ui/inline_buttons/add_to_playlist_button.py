from typing import Match, Optional

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType
from tase.errors import (
    PlaylistDoesNotExists,
    HitDoesNotExists,
    HitNoLinkedAudio,
    InvalidAudioForInlineMode,
)
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType
from .common import populate_playlist_list


class AddToPlaylistInlineButton(InlineButton):
    name = "add_to_playlist"
    type = InlineButtonType.ADD_TO_PLAYLIST

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{s_add_to_playlist} | {emoji._plus}"

    def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        results = populate_playlist_list(
            from_user, handler, result, telegram_inline_query
        )

        if len(results):
            result.results = results

    def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):
        hit_download_url = reg.group("arg1")
        # todo: check if the user has downloaded this audio earlier, otherwise, the request is not valid

        result_id_list = telegram_chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            handler.db.document.create_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PLAYLIST,
                state_dict={
                    "hit_download_url": hit_download_url,
                },
            )

            client.send_message(
                from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line",
            )
        else:
            # add the audio to the playlist
            try:
                successful, created = handler.db.graph.add_audio_to_playlist(
                    from_user,
                    playlist_key,
                    hit_download_url,
                )
            except PlaylistDoesNotExists as e:
                client.send_message(
                    from_user.user_id,
                    "You do not have the playlist you have chosen",
                )
            except HitDoesNotExists as e:
                client.send_message(
                    from_user.user_id,
                    "Given download url is not valid anymore",
                )
            except HitNoLinkedAudio as e:
                client.send_message(
                    from_user.user_id,
                    "Audio does not exist anymore",
                )
            except InvalidAudioForInlineMode as e:
                client.send_message(
                    from_user.user_id,
                    "This audio cannot be used in inline mode",
                )
            except Exception as e:
                logger.exception(e)
                client.send_message(
                    from_user.user_id,
                    "Could not add the audio to the playlist due to internal error",
                )
            else:
                # todo: update these messages
                if successful:
                    if created:
                        client.send_message(
                            from_user.user_id,
                            "Added to the playlist",
                        )
                    else:
                        client.send_message(
                            from_user.user_id,
                            "It's already on the playlist",
                        )
                else:
                    client.send_message(
                        from_user.user_id,
                        "Did not add to the playlist",
                    )
