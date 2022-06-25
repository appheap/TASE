from typing import Match

import pyrogram

from .inline_button import InlineButton

# from ..handlers import BaseHandler
from ..inline_items import CreateNewPlaylistItem, PlaylistItem
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...db.document_models import BotTaskStatus, BotTaskType
from ...my_logger import logger
from ...utils import _trans, emoji


class AddToPlaylistInlineButton(InlineButton):
    name = "add_to_playlist"

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{s_add_to_playlist} | {emoji._plus}"

    switch_inline_query_current_chat = f"#add_to_playlist"

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

        db_playlists = db.get_user_playlists(
            db_from_user,
            offset=from_,
        )

        results = []

        if from_ == 0:
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

        # db_hit = db.get_hit_by_download_url(audio_download_url)
        # db_audio = db.get_audio_from_hit(db_hit)

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            # todo: fix this duplicate code
            db.create_bot_task(
                db_from_user.user_id,
                telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PLAYLIST,
                state_dict={
                    "audio_download_url": audio_download_url,
                },
            )

            client.send_message(
                db_from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line",
            )
        else:
            # add the audio to the playlist
            created, successful = db.add_audio_to_playlist(
                playlist_key,
                audio_download_url,
            )

            # todo: update these messages
            if successful:
                if created:
                    client.send_message(
                        db_from_user.user_id,
                        "Added to the playlist",
                    )
                else:
                    client.send_message(
                        db_from_user.user_id,
                        "It's already on the playlist",
                    )
            else:
                client.send_message(
                    db_from_user.user_id,
                    "Did not add to the playlist",
                )
