from typing import Match

import pyrogram

from .inline_button import InlineButton
from ..inline_items import AudioItem, NoDownloadItem, PlaylistItem
from ..telegram_client import TelegramClient
# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import _trans, emoji


class GetPlaylistAudioInlineButton(InlineButton):
    name = "get_playlist_audios"

    s_audios = _trans("Audios")
    text = f"{s_audios} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#get_playlist_audios"

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
        playlist_key = reg.group("arg1")

        from_ = 0
        if inline_query.offset is not None and len(inline_query.offset):
            from_ = int(inline_query.offset)

        results = []

        if from_ == 0:
            db_playlist = db.get_playlist_by_key(playlist_key)
            results.append(
                PlaylistItem.get_item(db_playlist, db_from_user, inline_query)
            )

        db_audios = db.get_playlist_audios(db_from_user, playlist_key, offset=from_)

        # todo: fix this
        chats_dict = handler.update_audio_cache(db_audios)

        for db_audio in db_audios:
            db_audio_file_cache = db.get_audio_file_from_cache(
                db_audio, telegram_client.telegram_id
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
                    [NoDownloadItem.get_item(db_from_user)], cache_time=1
                )
