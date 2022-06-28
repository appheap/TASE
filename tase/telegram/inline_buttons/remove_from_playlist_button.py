from typing import Match, Optional

import pyrogram

from .inline_button import InlineButton
from ..inline import CustomInlineQueryResult
from ..inline_items import PlaylistItem
from ...db import graph_models
from ...utils import _trans, emoji, get_timestamp


class RemoveFromPlaylistInlineButton(InlineButton):
    name = "remove_from_playlist"

    s_remove_from_playlist = _trans("Remove From Playlist")
    text = f"{s_remove_from_playlist} | {emoji._minus}"

    switch_inline_query_current_chat = f"#remove_from_playlist"

    def on_inline_query(
        self,
        handler: "BaseHandler",
        result: CustomInlineQueryResult,
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        inline_query: "pyrogram.types.InlineQuery",
        query_date: int,
        reg: Optional[Match] = None,
    ):
        audio_download_url = reg.group("arg1")
        valid = True if audio_download_url is not None else False

        db_playlists = handler.db.get_audio_playlists(
            db_from_user,
            audio_download_url,
            offset=result.from_,
        )

        results = []

        for db_playlist in db_playlists:
            results.append(
                PlaylistItem.get_item(
                    db_playlist,
                    db_from_user,
                    inline_query,
                )
            )

        if len(results) and valid:
            result.results = results
        # todo: what to show when user doesn't have any playlists yet or hasn't added this audio to any playlist

    def on_chosen_inline_query(
        self,
        handler: "BaseHandler",
        client: "pyrogram.Client",
        db_from_user: graph_models.vertices.User,
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
        reg: Match,
    ):
        audio_download_url = reg.group("arg1")
        # todo: check if the user has downloaded this audio earlier, otherwise, the request is not valid

        result_id_list = chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]

        # remove the audio from the playlist
        removed = handler.db.remove_audio_from_playlist(
            playlist_key,
            audio_download_url,
            deleted_at=get_timestamp(),
        )

        # todo: update these messages
        if removed:
            client.send_message(
                db_from_user.user_id,
                "Removed from the playlist",
            )
        else:
            client.send_message(
                db_from_user.user_id,
                "Did not remove from the playlist",
            )
