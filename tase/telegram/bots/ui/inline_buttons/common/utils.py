import collections
from typing import List, Deque

import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InlineQueryType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.bots.ui.inline_items import (
    CreateNewPlaylistItem,
    PlaylistItem,
    AudioItem,
)
from tase.telegram.update_handlers.base import BaseHandler


def populate_playlist_list(
    from_user: graph_models.vertices.User,
    handler: BaseHandler,
    result: CustomInlineQueryResult,
    telegram_inline_query: pyrogram.types.InlineQuery,
) -> List[pyrogram.types.InlineQueryResult]:
    """
    Populate a list with the given `User` playlists

    Parameters
    ----------
    from_user : graph_models.vertices.User
        User to populate playlists from
    handler : BaseHandler
        Handler that got this update at the first place
    result : CustomInlineQueryResult
        Result object to used for populating playlists
    telegram_inline_query : pyrogram.types.InlineQuery
        Telegram Inline Query object

    Returns
    -------
    list of pyrogram.types.InlineQueryResult
        List of InlineQueryResult objects


    """
    playlists = handler.db.graph.get_user_playlists(
        from_user,
        offset=result.from_,
    )

    results = collections.deque()

    if result.from_ == 0:
        results.append(
            CreateNewPlaylistItem.get_item(
                from_user,
                telegram_inline_query,
            )
        )
    for playlist in playlists:
        results.append(
            PlaylistItem.get_item(
                playlist,
                from_user,
                telegram_inline_query,
            )
        )
    return list(results)


def populate_audio_items(
    results: Deque[pyrogram.types.InlineQueryResult],
    audio_vertices: List[graph_models.vertices.Audio],
    from_user: graph_models.vertices.User,
    handler: BaseHandler,
    query_date: int,
    result: CustomInlineQueryResult,
    telegram_inline_query: pyrogram.types.InlineQuery,
) -> None:
    """
    Populate a list of `AudioItem` objects

    Parameters
    ----------
    results : Deque[pyrogram.types.InlineQueryResult]
        Deque of the InlineQueryResult objects to populate
    audio_vertices : List[graph_models.vertices.Audio]
        List of `Audio` vertices to use for creating the `Query` vertex
    from_user : graph_models.vertices.User
        `User` to create the query for
    handler : BaseHandler
        Handler which got this update at the first place
    query_date : int
        Timestamp which this query happened
    result : CustomInlineQueryResult
        Result object to used for populating playlists
    telegram_inline_query : pyrogram.types.InlineQuery
        Telegram Inline Query object
    """
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
                    handler.db.graph.audio_in_favorite_playlist(
                        from_user,
                        hit.download_url,
                    ),
                )
            )
    else:
        pass
