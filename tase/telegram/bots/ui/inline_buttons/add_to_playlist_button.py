from typing import Match, Optional

import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans, emoji
from .inline_button import InlineButton
from ..inline_items import CreateNewPlaylistItem, PlaylistItem


class AddToPlaylistInlineButton(InlineButton):
    name = "add_to_playlist"

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{s_add_to_playlist} | {emoji._plus}"

    switch_inline_query_current_chat = f"#add_to_playlist"

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
        db_playlists = handler.db.graph.get_user_playlists(
            from_user,
            offset=result.from_,
        )

        results = []

        if result.from_ == 0:
            results.append(
                CreateNewPlaylistItem.get_item(
                    from_user,
                    telegram_inline_query,
                )
            )

        for db_playlist in db_playlists:
            results.append(
                PlaylistItem.get_item(
                    db_playlist,
                    from_user,
                    telegram_inline_query,
                )
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

        # db_hit = db.get_hit_by_download_url(hit_download_url)
        # db_audio = db.get_audio_from_hit(db_hit)

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            # todo: fix this duplicate code
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
            except Exception as e:
                #  If the user does not have a playlist with the given playlist_key, or no hit exists with the given hit_download_url, or audio is not valid for inline mode ,or the hit does not have any audio linked to it.
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
