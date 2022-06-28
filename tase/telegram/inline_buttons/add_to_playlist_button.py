from typing import Match, Optional

import pyrogram

from .inline_button import InlineButton
from ..inline import CustomInlineQueryResult
from ..inline_items import CreateNewPlaylistItem, PlaylistItem
from ...db import graph_models
from ...db.document_models import BotTaskType
from ...utils import _trans, emoji


class AddToPlaylistInlineButton(InlineButton):
    name = "add_to_playlist"

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{s_add_to_playlist} | {emoji._plus}"

    switch_inline_query_current_chat = f"#add_to_playlist"

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
            result.results = results

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

        # db_hit = db.get_hit_by_download_url(audio_download_url)
        # db_audio = db.get_audio_from_hit(db_hit)

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            # todo: fix this duplicate code
            handler.db.create_bot_task(
                db_from_user.user_id,
                handler.telegram_client.telegram_id,
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
            created, successful = handler.db.add_audio_to_playlist(
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
