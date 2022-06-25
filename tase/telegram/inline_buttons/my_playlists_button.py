from typing import Match

import pyrogram

from .inline_button import InlineButton

# from ..handlers import BaseHandler
from ..inline_items import CreateNewPlaylistItem, NoPlaylistItem, PlaylistItem
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import _trans, emoji


class MyPlaylistsInlineButton(InlineButton):
    name = "my_playlists"

    s_my_playlists = _trans("My Playlists")
    text = f"{s_my_playlists} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#my_playlists"

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

        db_playlists = db.get_user_playlists(db_from_user, offset=from_)

        results = []

        if from_ == 0:
            results.append(CreateNewPlaylistItem.get_item(db_from_user, inline_query))

        for db_playlist in db_playlists:
            results.append(
                PlaylistItem.get_item(db_playlist, db_from_user, inline_query)
            )

        if len(results):
            try:
                next_offset = (
                    str(from_ + len(results) + 1) if len(results) > 1 else None
                )
                inline_query.answer(results, cache_time=1, next_offset=next_offset)
            except Exception as e:
                logger.exception(e)
        else:
            if from_ is None or from_ == 0:
                inline_query.answer(
                    [NoPlaylistItem.get_item(db_from_user)], cache_time=1
                )

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
        hit_download_url = reg.group("arg1")

        result_id_list = chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]

        # db_hit = db.get_hit_by_download_url(hit_download_url)
        # db_audio = db.get_audio_from_hit(db_hit)

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            pass
