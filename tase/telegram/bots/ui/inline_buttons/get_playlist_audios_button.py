from typing import Match, Optional

import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InlineQueryType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
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
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
    ):
        playlist_key = reg.group("arg1")

        results = []
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
            audio_vertices = handler.db.graph.get_playlist_audios(
                from_user,
                playlist_key,
                offset=result.from_,
            )

            audio_vertices = list(audio_vertices)

            # todo: fix this
            chats_dict = handler.update_audio_cache(audio_vertices)

            db_query, hits = handler.db.graph.get_or_create_query(
                handler.telegram_client.telegram_id,
                from_user,
                telegram_inline_query.query,
                query_date,
                audio_vertices,
                telegram_inline_query=telegram_inline_query,
                inline_query_type=InlineQueryType.COMMAND,
                next_offset=result.get_next_offset(),
            )

            if db_query and hits:
                for audio_vertex, hit in zip(audio_vertices, hits):
                    audio_doc = handler.db.document.get_audio_by_key(
                        handler.telegram_client.telegram_id,
                        audio_vertex.key,
                    )
                    es_audio_doc = handler.db.index.get_audio_by_id(audio_vertex.key)

                    if not audio_doc or not audio_vertex.valid_for_inline_search:
                        continue

                    results.append(
                        AudioItem.get_item(
                            audio_doc.file_id,
                            from_user,
                            es_audio_doc,
                            telegram_inline_query,
                            chats_dict,
                            hit,
                        )
                    )

        if len(results) and playlist_is_valid:
            result.results = results
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
