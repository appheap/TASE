import collections
from typing import Match, Optional

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.errors import PlaylistDoesNotExists
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType
from .common import populate_audio_items
from ..inline_items import PlaylistItem, NoDownloadItem


class GetPlaylistAudioInlineButton(InlineButton):
    name = "get_playlist_audios"
    type = InlineButtonType.GET_PLAYLIST_AUDIOS

    s_audios = _trans("Audio Files")
    text = f"{s_audios} | {emoji._headphone}"

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
        playlist_key = reg.group("arg1")

        results = collections.deque()
        playlist_is_valid = (
            False  # whether the requested playlist belongs to the user or not
        )

        if result.from_ == 0:
            playlist = handler.db.graph.get_user_playlist_by_key(
                from_user,
                playlist_key,
                filter_out_soft_deleted=True,
            )
            if playlist:
                playlist_is_valid = True
                results.append(
                    PlaylistItem.get_item(
                        playlist,
                        from_user,
                        telegram_inline_query,
                    )
                )
            else:
                playlist_is_valid = False
        else:
            playlist_is_valid = True

        if playlist_is_valid:
            try:
                audio_vertices = handler.db.graph.get_playlist_audios(
                    from_user,
                    playlist_key,
                    offset=result.from_,
                )
            except PlaylistDoesNotExists:
                # since it is already been checked that the playlist belongs to the user, this exception will not occur
                pass
            else:
                audio_vertices = list(audio_vertices)

                populate_audio_items(
                    results,
                    audio_vertices,
                    from_user,
                    handler,
                    query_date,
                    result,
                    telegram_inline_query,
                )

        if len(results) and playlist_is_valid:
            result.results = list(results)
        else:
            if result.from_ is None or result.from_ == 0:
                result.results = [NoDownloadItem.get_item(from_user)]

    def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        reg: Match,
    ):

        result_id_list = telegram_chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        hit_download_url = result_id_list[1]

        # download_vertex = handler.db.graph.create_download(
        #     hit_download_url,
        #     from_user,
        #     handler.telegram_client.telegram_id,
        # )
        # if not download_vertex:
        #     # could not create the download
        #     logger.error("Could not create the `download` vertex:")
        #     logger.error(telegram_chosen_inline_result)
