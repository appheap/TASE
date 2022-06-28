from typing import Match, Optional

import pyrogram

from .inline_button import InlineButton
from ..inline import CustomInlineQueryResult
from ..inline_items import CreateNewPlaylistItem, NoPlaylistItem, PlaylistItem
from ...db import graph_models
from ...db.document_models import BotTaskType
from ...my_logger import logger
from ...utils import _trans, emoji


class MyPlaylistsInlineButton(InlineButton):
    name = "my_playlists"

    s_my_playlists = _trans("My Playlists")
    text = f"{s_my_playlists} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#my_playlists"

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

        db_playlists = handler.db.get_user_playlists(
            db_from_user,
            offset=result.from_,
        )

        results = []

        if result.from_ == 0:
            results.append(
                CreateNewPlaylistItem.get_item(
                    db_from_user,
                    inline_query,
                )
            )

        for db_playlist in db_playlists:
            results.append(
                PlaylistItem.get_item(
                    db_playlist,
                    db_from_user,
                    inline_query,
                )
            )

        if len(results):
            try:
                result.results = results
            except Exception as e:
                logger.exception(e)
        else:
            if result.from_ is None or result.from_ == 0:
                inline_query.answer(
                    [NoPlaylistItem.get_item(db_from_user)],
                    cache_time=1,
                )

    def on_chosen_inline_query(
        self,
        handler: "BaseHandler",
        client: "pyrogram.Client",
        db_from_user: graph_models.vertices.User,
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
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
            # todo: fix this duplicate code
            handler.db.create_bot_task(
                db_from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PLAYLIST,
            )

            client.send_message(
                db_from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line",
            )
