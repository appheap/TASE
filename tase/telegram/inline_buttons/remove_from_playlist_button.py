from typing import Match

import pyrogram

from .inline_button import InlineButton
# from ..handlers import BaseHandler
from ..inline_items import PlaylistItem
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import _trans, emoji, get_timestamp


class RemoveFromPlaylistInlineButton(InlineButton):
    name = "remove_from_playlist"

    s_remove_from_playlist = _trans("Remove From Playlist")
    text = f"{s_remove_from_playlist} | {emoji._minus}"

    switch_inline_query_current_chat = f"#remove_from_playlist"

    def on_inline_query(
        self,
        client: "pyrogram.Client",
        inline_query: "pyrogram.types.InlineQuery",
        handler: "BaseHandler",
        db: "DatabaseClient",
        telegram_client: "TelegramClient",
        db_from_user: graph_models.vertices.User,
        reg: Match,
    ):
        from_ = 0
        if inline_query.offset is not None and len(inline_query.offset):
            from_ = int(inline_query.offset)

        audio_download_url = reg.group("arg1")
        valid = True if audio_download_url is not None else False

        db_playlists = db.get_audio_playlists(
            db_from_user,
            audio_download_url,
            offset=from_,
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
            try:
                next_offset = (
                    str(from_ + len(results) + 1) if len(results) > 1 else None
                )
                inline_query.answer(
                    results,
                    cache_time=1,
                    next_offset=next_offset,
                )
            except Exception as e:
                logger.exception(e)

    def on_chosen_inline_query(
        self,
        client: "pyrogram.Client",
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
        handler: "BaseHandler",
        db: "DatabaseClient",
        telegram_client: "TelegramClient",
        db_from_user: graph_models.vertices.User,
        reg: Match,
    ):
        audio_download_url = reg.group("arg1")
        # todo: check if the user has downloaded this audio earlier, otherwise, the request is not valid

        result_id_list = chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]

        # remove the audio from the playlist
        removed = db.remove_audio_from_playlist(
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
