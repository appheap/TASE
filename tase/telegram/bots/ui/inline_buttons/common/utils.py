import asyncio
import collections
import functools
from typing import Deque, Optional, Union

import pyrogram
from pyrogram.types import InlineKeyboardMarkup

from tase.common.utils import async_timed
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType, InlineQueryType
from tase.db.arangodb.helpers import AudioKeyboardStatus
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType
from tase.telegram.bots.ui.inline_buttons import (
    AddToPlaylistInlineButton,
    BackToPlaylistsInlineButton,
    DeletePlaylistInlineButton,
    DownloadAudioInlineButton,
    EditPlaylistDescriptionInlineButton,
    EditPlaylistTitleInlineButton,
    GetPlaylistAudioInlineButton,
    HomeInlineButton,
    RemoveFromPlaylistInlineButton,
    SearchAmongPublicPlaylistsInlineButton,
    SharePlaylistInlineButton,
    ShowMoreResultsInlineButton,
    TogglePlaylistSettingsInlineButton,
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
    from tase.telegram.bots.ui.inline_items import CreateNewPrivatePlaylistItem, PlaylistItem

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
    inline_query_type: InlineQueryType,
    playlist_key: Optional[str] = None,
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
    inline_query_type : InlineQueryType
        Type of inline query.
    playlist_key : str
        Key of the playlist where this audio downloaded from.
    """
    if not audio_vertices:
        return collections.deque()

    from tase.telegram.bots.ui.inline_items import AudioItem

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
                inline_query_type,
                playlist_key=playlist_key,
            )
            for audio_doc, audio_vertex, hit_download_url, in zip(audio_docs, audio_vertices, hit_download_urls)
            if audio_doc and audio_vertex and audio_doc.key not in invalid_audio_keys
        )
    )

    return hit_download_urls


def get_download_audio_keyboard(
    from_user: graph_models.vertices.User,
    bot_username: str,
    link: str,
) -> InlineKeyboardMarkup:
    from tase.telegram.bots.ui.inline_buttons import DownloadAudioInlineButton

    return InlineKeyboardMarkup(
        [
            [
                DownloadAudioInlineButton.get_keyboard(
                    url=f"https://t.me/{bot_username}?start={link}",
                    lang_code=from_user.chosen_language_code,
                ),
            ]
        ]
    )


def get_audio_markup_keyboard(
    bot_username: str,
    chat_type: ChatType,
    chosen_language_code: str,
    hit_download_url: str,
    status: AudioKeyboardStatus,
    playlist_key: Optional[str] = None,
    inline_button_type: Optional[InlineButtonType] = InlineButtonType.NOT_A_BUTTON,
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
    status : AudioKeyboardStatus
        Keyboard status of this audio file
    playlist_key : str, optional
        Key of the playlist vertex this audio downloaded from.
    inline_button_type : InlineButtonType, default : InlineButtonType.NOT_A_BUTTON
        Type of the inline button which this query was made from. It is only meant for queries made outside BOT chat. Moreover, it needs to be a valid type
        declared in one of the subclasses of `BaseAudioLinkData` class.

    Returns
    -------
    InlineKeyboardMarkup
        Markup keyboard for the audio message

    """
    if chat_type == ChatType.BOT:
        markup = [
            [
                AddToPlaylistInlineButton.get_keyboard(
                    hit_download_url=hit_download_url,
                    lang_code=chosen_language_code,
                ),
                RemoveFromPlaylistInlineButton.get_keyboard(
                    hit_download_url=hit_download_url,
                    lang_code=chosen_language_code,
                ),
                InlineButton.get_button(InlineButtonType.ADD_TO_FAVORITE_PLAYLIST)
                .change_text(status.is_in_favorite_playlist)
                .get_keyboard(
                    chat_type=chat_type,
                    hit_download_url=hit_download_url,
                    lang_code=chosen_language_code,
                ),
            ],
            [
                InlineButton.get_button(InlineButtonType.DISLIKE_AUDIO)
                .change_text(status.is_disliked)
                .get_keyboard(
                    chat_type=chat_type,
                    hit_download_url=hit_download_url,
                    lang_code=chosen_language_code,
                    playlist_key=playlist_key,
                ),
                InlineButton.get_button(InlineButtonType.LIKE_AUDIO)
                .change_text(status.is_liked)
                .get_keyboard(
                    chat_type=chat_type,
                    hit_download_url=hit_download_url,
                    lang_code=chosen_language_code,
                    playlist_key=playlist_key,
                ),
            ],
            [
                HomeInlineButton.get_keyboard(lang_code=chosen_language_code),
            ],
        ]
        markup = InlineKeyboardMarkup(markup)
    else:
        from tase.telegram.bots.ui.base import AudioLinkData

        markup = [
            [
                DownloadAudioInlineButton.get_keyboard(
                    url=f"https://t.me/{bot_username}?start={AudioLinkData.generate_data(hit_download_url, playlist_key, inline_button_type)}",
                    lang_code=chosen_language_code,
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
            ShowMoreResultsInlineButton.get_keyboard(
                query_hash=u,
                query=query,
                lang_code=chosen_language_code,
            ),
        ],
    ]
    return InlineKeyboardMarkup(markup)


async def update_playlist_keyboard_markup(
    db: DatabaseClient,
    client: pyrogram.Client,
    from_user: graph_models.vertices.User,
    telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
    playlist_item: "PlaylistItemInfo",
):
    if playlist_item.is_public:
        playlist = await db.index.get_playlist_by_id(playlist_item.playlist_key)
    else:
        playlist = await db.graph.get_playlist_by_key(playlist_item.playlist_key)

    from tase.telegram.bots.ui.inline_buttons.common import get_playlist_markup_keyboard

    await client.edit_inline_reply_markup(
        telegram_chosen_inline_result.inline_message_id,
        reply_markup=get_playlist_markup_keyboard(
            playlist,
            from_user,
            playlist_item.chat_type,
            has_subscribed=await db.graph.has_user_subscribed_to_playlist(from_user, playlist_item.playlist_key),
        ),
    )


def get_playlist_loading_keyboard(
    playlist_key: str,
    is_public: bool,
    lang_code: Optional[str] = "en",
) -> InlineKeyboardMarkup:
    from tase.telegram.bots.ui.inline_buttons import PlaylistLoadingKeyboardInlineButton

    return InlineKeyboardMarkup(
        [
            [
                PlaylistLoadingKeyboardInlineButton.get_keyboard(
                    playlist_key=playlist_key,
                    is_public=is_public,
                    lang_code=lang_code,
                ),
            ]
        ]
    )


def get_audio_loading_keyboard(
    hit_download_url: str,
    lang_code: Optional[str] = "en",
) -> InlineKeyboardMarkup:
    from tase.telegram.bots.ui.inline_buttons import AudioLoadingKeyboardInlineButton

    return InlineKeyboardMarkup(
        [
            [
                AudioLoadingKeyboardInlineButton.get_keyboard(
                    hit_download_url=hit_download_url,
                    lang_code=lang_code,
                ),
            ]
        ]
    )


def get_playlist_markup_keyboard(
    playlist: Union[graph_models.vertices.Playlist, elasticsearch_models.Playlist],
    user: graph_models.vertices.User,
    chat_type: ChatType,
    is_settings_visible: Optional[bool] = False,
    has_subscribed: Optional[bool] = None,
) -> InlineKeyboardMarkup:
    """
    Get markup keyboard for a playlist

    Parameters
    ----------
    playlist : graph_models.vertices.Playlist
        Playlist vertex object.
    user : graph_models.vertices.User
        User that initiated this request.
    chat_type : ChatType
        Type of the chat this request originated from.
    is_settings_visible : bool, default : False
        Whether to show settings for non-favorite playlists or not.
    has_subscribed : bool, optional
        Whether the user has subscribed to this playlist or not. (It is only meant for public playlists)

    Returns
    -------
    InlineKeyboardMarkup
        Markup keyboard for the playlist

    """
    is_public = True if isinstance(playlist, elasticsearch_models.Playlist) else playlist.is_public
    is_favorite = False if isinstance(playlist, elasticsearch_models.Playlist) else playlist.is_favorite
    playlist_key = playlist.id if isinstance(playlist, elasticsearch_models.Playlist) else playlist.key

    if not is_public:
        if is_favorite:
            markup = [
                [
                    GetPlaylistAudioInlineButton.get_keyboard(
                        playlist_key=playlist_key,
                        lang_code=user.chosen_language_code,
                    ),
                    # todo: add a button to get the top 10 audios from this playlist as a message
                ],
                [
                    HomeInlineButton.get_keyboard(lang_code=user.chosen_language_code),
                    BackToPlaylistsInlineButton.get_keyboard(lang_code=user.chosen_language_code),
                ],
            ]
        else:
            markup = [
                [
                    GetPlaylistAudioInlineButton.get_keyboard(
                        lang_code=user.chosen_language_code,
                        playlist_key=playlist_key,
                    ),
                ],
                [
                    HomeInlineButton.get_keyboard(lang_code=user.chosen_language_code),
                    BackToPlaylistsInlineButton.get_keyboard(lang_code=user.chosen_language_code),
                    TogglePlaylistSettingsInlineButton.get_keyboard(
                        playlist_key=playlist_key,
                        is_settings_visible=is_settings_visible,
                        lang_code=user.chosen_language_code,
                    ),
                ],
            ]

        if is_settings_visible:
            markup.append(
                [
                    EditPlaylistTitleInlineButton.get_keyboard(
                        playlist_key=playlist_key,
                        lang_code=user.chosen_language_code,
                    ),
                    EditPlaylistDescriptionInlineButton.get_keyboard(
                        playlist_key=playlist_key,
                        lang_code=user.chosen_language_code,
                    ),
                ],
            )
            markup.append(
                [
                    DeletePlaylistInlineButton.get_keyboard(playlist_key=playlist_key, lang_code=user.chosen_language_code),
                ],
            )
    else:
        markup = [
            [
                GetPlaylistAudioInlineButton.get_keyboard(
                    lang_code=user.chosen_language_code,
                    playlist_key=playlist_key,
                ),
            ],
            [
                InlineButton.get_button(InlineButtonType.TOGGLE_PLAYLIST_SUBSCRIPTION)
                .change_text(has_subscribed=has_subscribed)
                .get_keyboard(
                    playlist_key=playlist_key,
                    lang_code=user.chosen_language_code,
                ),
                SharePlaylistInlineButton.get_keyboard(
                    playlist_key=playlist_key,
                    lang_code=user.chosen_language_code,
                ),
            ],
            [
                SearchAmongPublicPlaylistsInlineButton.get_keyboard(lang_code=user.chosen_language_code),
            ],
        ]
        if user.user_id == playlist.owner_user_id and chat_type == ChatType.BOT:
            markup.append(
                [
                    TogglePlaylistSettingsInlineButton.get_keyboard(
                        playlist_key=playlist_key,
                        is_settings_visible=is_settings_visible,
                        lang_code=user.chosen_language_code,
                    ),
                ]
            )
            if is_settings_visible:
                markup.append(
                    [
                        EditPlaylistTitleInlineButton.get_keyboard(
                            playlist_key=playlist_key,
                            lang_code=user.chosen_language_code,
                        ),
                        EditPlaylistDescriptionInlineButton.get_keyboard(
                            playlist_key=playlist_key,
                            lang_code=user.chosen_language_code,
                        ),
                    ],
                )
                markup.append(
                    [
                        DeletePlaylistInlineButton.get_keyboard(playlist_key=playlist_key, lang_code=user.chosen_language_code),
                    ],
                )

    return InlineKeyboardMarkup(markup)
