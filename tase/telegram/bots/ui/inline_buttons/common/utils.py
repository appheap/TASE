import collections
from typing import List, Deque

import pyrogram
from pyrogram.types import InlineKeyboardMarkup

from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InlineQueryType, InteractionType, ChatType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.bots.ui.inline_buttons.base import InlineButton, InlineButtonType
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
    filter_by_capacity: bool = False,
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
    filter_by_capacity : bool, default : False
        Whether to filter the playlists by their length

    Returns
    -------
    list of pyrogram.types.InlineQueryResult
        List of InlineQueryResult objects


    """
    playlists = (
        handler.db.graph.get_user_valid_playlists(
            from_user,
            offset=result.from_,
        )
        if filter_by_capacity
        else handler.db.graph.get_user_playlists(
            from_user,
            offset=result.from_,
        )
    )

    results = collections.deque()

    user_playlist_count = handler.db.graph.get_user_playlists_count(from_user)

    if result.from_ == 0 and user_playlist_count < 11:
        # a total number of 10 playlists is allowed for each user (favorite playlist excluded)
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
                    handler.telegram_client.get_me().username,
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
                    handler.db.graph.audio_is_interacted_by_user(
                        from_user,
                        hit.download_url,
                        InteractionType.DISLIKE,
                    ),
                    handler.db.graph.audio_is_interacted_by_user(
                        from_user,
                        hit.download_url,
                        InteractionType.LIKE,
                    ),
                )
            )
    else:
        pass


def get_audio_markup_keyboard(
    bot_username: str,
    chat_type: ChatType,
    chosen_language_code: str,
    hit_download_url: str,
    valid_for_inline_search: bool,
    audio_in_favorite_playlist: bool,
    audio_is_disliked: bool,
    audio_is_liked: bool,
) -> InlineKeyboardMarkup:
    """
    Get markup keyboard for an audio message

    Parameters
    ----------
    bot_username : str
        Username of the BOT queried
    chat_type : ChatType
        Type of the chat this audio message is sent to
    chosen_language_code : str
        Language code the user that ran this query
    hit_download_url : str
        Download URL of the hit
    valid_for_inline_search : bool
        Whether this audio is valid for inline mode or not
    audio_in_favorite_playlist : bool
        Whether this audio belongs to the user's favorite playlist or not
    audio_is_disliked : bool
        Whether this audio is disliked by the user or not
    audio_is_liked : bool
        Whether this audio is liked by the user or not

    Returns
    -------
    InlineKeyboardMarkup
        Markup keyboard for the audio message

    """
    if chat_type == ChatType.BOT:
        if valid_for_inline_search:
            markup = [
                [
                    InlineButton.get_button(
                        InlineButtonType.ADD_TO_PLAYLIST
                    ).get_inline_keyboard_button(
                        chosen_language_code,
                        hit_download_url,
                    ),
                    InlineButton.get_button(
                        InlineButtonType.REMOVE_FROM_PLAYLIST
                    ).get_inline_keyboard_button(
                        chosen_language_code,
                        hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.ADD_TO_FAVORITE_PLAYLIST)
                    .change_text(audio_in_favorite_playlist)
                    .get_inline_keyboard_button(
                        chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                ],
                [
                    InlineButton.get_button(InlineButtonType.DISLIKE_AUDIO)
                    .change_text(audio_is_disliked)
                    .get_inline_keyboard_button(
                        chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.LIKE_AUDIO)
                    .change_text(audio_is_liked)
                    .get_inline_keyboard_button(
                        chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                ],
                [
                    InlineButton.get_button(
                        InlineButtonType.HOME
                    ).get_inline_keyboard_button(
                        chosen_language_code,
                    ),
                ],
            ]
        else:
            markup = [
                [
                    InlineButton.get_button(InlineButtonType.DISLIKE_AUDIO)
                    .change_text(audio_is_disliked)
                    .get_inline_keyboard_button(
                        chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.LIKE_AUDIO)
                    .change_text(audio_is_liked)
                    .get_inline_keyboard_button(
                        chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                ],
                [
                    InlineButton.get_button(
                        InlineButtonType.HOME
                    ).get_inline_keyboard_button(
                        chosen_language_code,
                    ),
                ],
            ]

        markup = InlineKeyboardMarkup(markup)
    else:
        markup = [
            [
                InlineButton.get_button(
                    InlineButtonType.DOWNLOAD_AUDIO
                ).get_inline_keyboard_button(
                    chosen_language_code,
                    url=f"https://t.me/{bot_username}?start=dl_{hit_download_url}",
                ),
            ]
        ]
        markup = InlineKeyboardMarkup(markup)

    return markup


def get_playlist_markup_keyboard(
    playlist: graph_models.vertices.Playlist,
    chosen_language_code: str,
) -> InlineKeyboardMarkup:
    """
    Get markup keyboard for a playlist

    Parameters
    ----------
    playlist : graph_models.vertices.Playlist
        Playlist vertex object
    chosen_language_code : str
        Language code chosen by the user who owns this playlist

    Returns
    -------
    InlineKeyboardMarkup
        Markup keyboard for the playlist

    """
    if playlist.is_favorite:
        markup = [
            [
                InlineButton.get_button(
                    InlineButtonType.GET_PLAYLIST_AUDIOS
                ).get_inline_keyboard_button(
                    chosen_language_code,
                    playlist.key,
                ),
                # todo: add a button to get the top 10 audios from this playlist as a message
            ],
            [
                InlineButton.get_button(
                    InlineButtonType.HOME
                ).get_inline_keyboard_button(
                    chosen_language_code,
                ),
                InlineButton.get_button(
                    InlineButtonType.BACK_TO_PLAYLISTS
                ).get_inline_keyboard_button(
                    chosen_language_code,
                ),
            ],
        ]
    else:
        markup = [
            [
                InlineButton.get_button(
                    InlineButtonType.HOME
                ).get_inline_keyboard_button(chosen_language_code),
                InlineButton.get_button(
                    InlineButtonType.BACK_TO_PLAYLISTS
                ).get_inline_keyboard_button(chosen_language_code),
            ],
            [
                InlineButton.get_button(
                    InlineButtonType.GET_PLAYLIST_AUDIOS
                ).get_inline_keyboard_button(
                    chosen_language_code,
                    playlist.key,
                ),
                # todo: add a button to get the top 10 audios from this playlist as a message
            ],
            [
                InlineButton.get_button(
                    InlineButtonType.EDIT_PLAYLIST_TITLE
                ).get_inline_keyboard_button(
                    chosen_language_code,
                    playlist.key,
                    callback_arg=playlist.key,
                ),
                InlineButton.get_button(
                    InlineButtonType.EDIT_PLAYLIST_DESCRIPTION
                ).get_inline_keyboard_button(
                    chosen_language_code,
                    playlist.key,
                    callback_arg=playlist.key,
                ),
            ],
            [
                InlineButton.get_button(
                    InlineButtonType.DELETE_PLAYLIST
                ).get_inline_keyboard_button(
                    chosen_language_code,
                    playlist.key,
                    callback_arg=playlist.key,
                ),
            ],
        ]

    return InlineKeyboardMarkup(markup)
