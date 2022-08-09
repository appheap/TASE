from typing import Match, Optional

import pyrogram

from tase.db import graph_models
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.utils import _trans, emoji
from .inline_button import InlineButton
from ..inline_items import PlaylistItem, AudioItem, NoDownloadItem


class GetPlaylistAudioInlineButton(InlineButton):
    name = "get_playlist_audios"

    s_audios = _trans("Audio Files")
    text = f"{s_audios} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#get_playlist_audios"

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
        playlist_key = reg.group("arg1")

        results = []
        playlist_is_valid = False  # whether the requested playlist belongs to the user or not

        if result.from_ == 0:
            db_playlist = handler.db.get_playlist_by_key(playlist_key)
            db_playlists = handler.db.get_user_playlists(
                db_from_user,
                offset=0,
                limit=100,
            )
            for db_pl in db_playlists:
                if db_pl.key == db_playlist.key:
                    # playlist belongs to the user
                    playlist_is_valid = True
                    break

            if playlist_is_valid:
                results.append(
                    PlaylistItem.get_item(
                        db_playlist,
                        db_from_user,
                        inline_query,
                    )
                )
        else:
            playlist_is_valid = True

        if playlist_is_valid:
            db_audios = handler.db.get_playlist_audios(
                db_from_user,
                playlist_key,
                offset=result.from_,
            )

            # todo: fix this
            chats_dict = handler.update_audio_cache(db_audios)

            for db_audio in db_audios:
                db_audio_file_cache = handler.db.get_audio_file_from_cache(
                    db_audio,
                    handler.telegram_client.telegram_id,
                )

                #  todo: Some audios have null titles, solution?
                if not db_audio_file_cache or not db_audio.title:
                    continue

                results.append(
                    AudioItem.get_item(
                        db_audio_file_cache,
                        db_from_user,
                        db_audio,
                        inline_query,
                        chats_dict,
                    )
                )

        if len(results) and playlist_is_valid:
            result.results = results
        else:
            if result.from_ is None or result.from_ == 0:
                result.results = [NoDownloadItem.get_item(db_from_user)]
