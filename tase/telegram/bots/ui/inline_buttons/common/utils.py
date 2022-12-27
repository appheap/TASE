import asyncio
import collections
import functools
from typing import Deque, Optional

import pyrogram
from pyrogram.types import InlineKeyboardMarkup

from tase.common.utils import async_timed
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.bots.ui.inline_buttons.base import InlineButton, InlineButtonType
from tase.telegram.bots.ui.inline_items import (
    CreateNewPrivatePlaylistItem,
    PlaylistItem,
    AudioItem,
)
from tase.telegram.update_handlers.base import BaseHandler


@async_timed()
async def populate_playlist_list(
    from_user: graph_models.vertices.User,
    handler: BaseHandler,
    result: CustomInlineQueryResult,
    telegram_inline_query: pyrogram.types.InlineQuery,
    filter_by_capacity: Optional[bool] = False,
    view_playlist: Optional[bool] = True,
) -> None:
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
    view_playlist : bool, default : True
        Whether to show playlist item when clicked or not.

    """
    playlists = (
        await handler.db.graph.get_user_valid_playlists(
            from_user,
            offset=result.from_,
        )
        if filter_by_capacity
        else await handler.db.graph.get_user_playlists(
            from_user,
            offset=result.from_,
        )
    )

    user_playlist_count = await handler.db.graph.get_user_playlists_count(from_user)

    if result.is_first_page() and user_playlist_count < 11:
        # a total number of 10 playlists is allowed for each user (favorite playlist excluded)
        result.add_item(
            CreateNewPrivatePlaylistItem.get_item(
                from_user,
                telegram_inline_query,
            ),
            count=False,
        )

    for playlist in playlists:
        result.add_item(
            PlaylistItem.get_item(
                playlist,
                from_user,
                telegram_inline_query,
                view_playlist=view_playlist,
            )
        )


@async_timed()
async def populate_audio_items(
    audio_vertices: Deque[graph_models.vertices.Audio],
    from_user: graph_models.vertices.User,
    handler: BaseHandler,
    result: CustomInlineQueryResult,
    telegram_inline_query: pyrogram.types.InlineQuery,
) -> Deque[str]:
    """
    Populate a list of `AudioItem` objects

    Parameters
    ----------
    audio_vertices : Deque[graph_models.vertices.Audio]
        List of `Audio` vertices to use for creating the `Query` vertex
    from_user : graph_models.vertices.User
        `User` to create the query for
    handler : BaseHandler
        Handler which got this update at the first place
    result : CustomInlineQueryResult
        Result object to used for populating playlists
    telegram_inline_query : pyrogram.types.InlineQuery
        Telegram Inline Query object
    """
    if not audio_vertices:
        return collections.deque()

    # todo: fix this
    chats_dict, invalid_audio_keys = await handler.update_audio_cache(audio_vertices)

    audio_docs = await asyncio.gather(
        *(
            handler.db.document.get_audio_by_key(
                audio_vertex.get_doc_cache_key(handler.telegram_client.telegram_id),
            )
            for audio_vertex in audio_vertices
        )
    )
    hit_download_urls = await handler.db.graph.generate_hit_download_urls(size=len(audio_vertices))

    username = (await handler.telegram_client.get_me()).username

    result.extend_results(
        (
            AudioItem.get_item(
                username,
                audio_doc.file_id,
                from_user,
                audio_vertex,
                telegram_inline_query,
                chats_dict,
                hit_download_url,
            )
            for audio_doc, audio_vertex, hit_download_url, in zip(audio_docs, audio_vertices, hit_download_urls)
            if audio_doc and audio_vertex and audio_doc.key not in invalid_audio_keys
        )
    )

    return hit_download_urls


def get_audio_markup_keyboard(
    bot_username: str,
    chat_type: ChatType,
    chosen_language_code: str,
    hit_download_url: str,
    valid_for_inline_search: bool,
    status: AudioKeyboardStatus,
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
    status : AudioKeyboardStatus
        Keyboard status of this audio file

    Returns
    -------
    InlineKeyboardMarkup
        Markup keyboard for the audio message

    """
    if chat_type == ChatType.BOT:
        if valid_for_inline_search:
            markup = [
                [
                    InlineButton.get_button(InlineButtonType.ADD_TO_PLAYLIST).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        switch_inline_arg=hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.REMOVE_FROM_PLAYLIST).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        switch_inline_arg=hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.ADD_TO_FAVORITE_PLAYLIST)
                    .change_text(status.is_in_favorite_playlist)
                    .get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                ],
                [
                    InlineButton.get_button(InlineButtonType.DISLIKE_AUDIO)
                    .change_text(status.is_disliked)
                    .get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.LIKE_AUDIO)
                    .change_text(status.is_liked)
                    .get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                ],
                [
                    InlineButton.get_button(InlineButtonType.HOME).get_inline_keyboard_button(lang_code=chosen_language_code),
                ],
            ]
        else:
            markup = [
                [
                    InlineButton.get_button(InlineButtonType.DISLIKE_AUDIO)
                    .change_text(status.is_disliked)
                    .get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                    InlineButton.get_button(InlineButtonType.LIKE_AUDIO)
                    .change_text(status.is_liked)
                    .get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=hit_download_url,
                    ),
                ],
                [
                    InlineButton.get_button(InlineButtonType.HOME).get_inline_keyboard_button(lang_code=chosen_language_code),
                ],
            ]

        markup = InlineKeyboardMarkup(markup)
    else:
        markup = [
            [
                InlineButton.get_button(InlineButtonType.DOWNLOAD_AUDIO).get_inline_keyboard_button(
                    lang_code=chosen_language_code,
                    url=f"https://t.me/{bot_username}?start=dl_{hit_download_url}",
                ),
            ]
        ]
        markup = InlineKeyboardMarkup(markup)

    return markup


def add(v1: int, v2: int) -> int:
    """
    Add two integers and return the result.

    Parameters
    ----------
    v1 : int
        Integer number one.
    v2 : int
        Integer number two.

    Returns
    -------
    int
        Calculated sum of the given integers.

    """
    return v1 + v2


def get_query_hash(query: str) -> Optional[str]:
    """
    Calculate a hash for the given `query` string.

    Parameters
    ----------
    query : str,
        Query string to calculate the hash for.

    Returns
    -------
    str, optional
        Calculated hash if operation was successful, otherwise return None.

    """
    if not query:
        return None

    query = query.strip()
    if not query:
        return None

    u = functools.reduce(add, (idx * ord(c) for idx, c in enumerate(query, 1)))
    u = str(hex(u))[2:]

    return u


def get_more_results_markup_keyboad(
    chosen_language_code: str,
    query: str,
):
    query = query.strip()
    if not query:
        return None

    u = get_query_hash(query)
    if not u:
        return None

    markup = [
        [
            InlineButton.get_button(InlineButtonType.SHOW_MORE_RESULTS).get_inline_keyboard_button(
                lang_code=chosen_language_code,
                switch_inline_arg=u + " \u200c " + query,
            ),
        ],
    ]
    return InlineKeyboardMarkup(markup)


def get_playlist_markup_keyboard(
    playlist: graph_models.vertices.Playlist,
    chosen_language_code: str,
    is_settings_visible: Optional[bool] = False,
) -> InlineKeyboardMarkup:
    """
    Get markup keyboard for a playlist

    Parameters
    ----------
    playlist : graph_models.vertices.Playlist
        Playlist vertex object
    chosen_language_code : str
        Language code chosen by the user who owns this playlist
    is_settings_visible : bool, default : False
        Whether to show settings for non-favorite playlists or not.

    Returns
    -------
    InlineKeyboardMarkup
        Markup keyboard for the playlist

    """
    if not playlist.is_public:
        if playlist.is_favorite:
            markup = [
                [
                    InlineButton.get_button(InlineButtonType.GET_PLAYLIST_AUDIOS).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        switch_inline_arg=playlist.key,
                    ),
                    # todo: add a button to get the top 10 audios from this playlist as a message
                ],
                [
                    InlineButton.get_button(InlineButtonType.HOME).get_inline_keyboard_button(lang_code=chosen_language_code),
                    InlineButton.get_button(InlineButtonType.BACK_TO_PLAYLISTS).get_inline_keyboard_button(lang_code=chosen_language_code),
                ],
            ]
        else:
            markup = [
                [
                    InlineButton.get_button(InlineButtonType.GET_PLAYLIST_AUDIOS).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        switch_inline_arg=playlist.key,
                    ),
                    # todo: add a button to get the top 10 audios from this playlist as a message
                ],
                [
                    InlineButton.get_button(InlineButtonType.HOME).get_inline_keyboard_button(lang_code=chosen_language_code),
                    InlineButton.get_button(InlineButtonType.BACK_TO_PLAYLISTS).get_inline_keyboard_button(lang_code=chosen_language_code),
                    InlineButton.get_button(InlineButtonType.TOGGLE_PLAYLIST_SETTINGS).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=f"{playlist.key}#{'1' if is_settings_visible else '0'}",
                    ),
                ],
            ]

        if is_settings_visible:
            markup.append(
                [
                    InlineButton.get_button(InlineButtonType.EDIT_PLAYLIST_TITLE).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=playlist.key,
                    ),
                    InlineButton.get_button(InlineButtonType.EDIT_PLAYLIST_DESCRIPTION).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=playlist.key,
                    ),
                ],
            )
            markup.append(
                [
                    InlineButton.get_button(InlineButtonType.DELETE_PLAYLIST).get_inline_keyboard_button(
                        lang_code=chosen_language_code,
                        callback_arg=playlist.key,
                    ),
                ],
            )
    else:
        markup = [
            [
                InlineButton.get_button(InlineButtonType.GET_PLAYLIST_AUDIOS).get_inline_keyboard_button(
                    lang_code=chosen_language_code,
                    switch_inline_arg=playlist.key,
                ),
            ],
            [
                InlineButton.get_button(InlineButtonType.TOGGLE_PLAYLIST_SUBSCRIPTION).get_inline_keyboard_button(
                    lang_code=chosen_language_code,
                    callback_arg=playlist.key,
                ),
                InlineButton.get_button(InlineButtonType.SHARE_PLAYLIST).get_inline_keyboard_button(
                    lang_code=chosen_language_code,
                    switch_inline_arg=playlist.key,
                ),
            ],
        ]

    return InlineKeyboardMarkup(markup)
