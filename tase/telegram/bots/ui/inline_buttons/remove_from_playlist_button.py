import collections
from typing import Match, Optional

import pyrogram

from tase.common.utils import _trans, emoji, get_now_timestamp
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
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
from ..inline_items import PlaylistItem


class RemoveFromPlaylistInlineButton(InlineButton):
    name = "remove_from_playlist"
    type = InlineButtonType.REMOVE_FROM_PLAYLIST

    s_remove_from_playlist = _trans("Remove From Playlist")
    text = f"{emoji._minus}"
    is_inline = True

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
        hit_download_url = reg.group("arg1")
        valid = True if hit_download_url is not None else False

        results = collections.deque()

        try:
            db_playlists = handler.db.graph.get_audio_playlists(
                from_user,
                hit_download_url,
                offset=result.from_,
            )
        except HitNoLinkedAudio:
            # fixme: this happen if the hit with the given `download_url` does not have any audio vertex linked to
            #  it. notify the user about this situation and update the database
            client.send_message(
                from_user.user_id,
                "Given download url is not valid anymore",
            )
        else:
            for playlist in db_playlists:
                results.append(
                    PlaylistItem.get_item(
                        playlist,
                        from_user,
                        telegram_inline_query,
                    )
                )

        if len(results) and valid:
            result.results = list(results)
        # todo: what to show when user doesn't have any playlists yet or hasn't added this audio to any playlist

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
        chat_type = ChatType(int(result_id_list[2]))

        # remove the audio from the playlist
        try:
            successful, removed = handler.db.graph.remove_audio_from_playlist(
                from_user,
                playlist_key,
                hit_download_url,
                get_now_timestamp(),
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
                "Could not remove the audio from the playlist",
            )
        else:
            # todo: update these messages
            if successful:
                if removed:
                    client.send_message(
                        from_user.user_id,
                        "Removed from the playlist",
                    )
                else:
                    client.send_message(
                        from_user.user_id,
                        "Did not remove from the playlist",
                    )
            else:
                client.send_message(
                    from_user.user_id,
                    "Did not remove from the playlist",
                )
