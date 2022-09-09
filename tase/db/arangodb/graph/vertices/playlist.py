from typing import Optional, Tuple, Generator

from pydantic import Field

from tase.my_logger import logger
from tase.utils import generate_token_urlsafe, prettify
from . import Audio
from .base_vertex import BaseVertex
from .user import User
from .. import ArangoGraphMethods
from ..edges import Has, Had
from ...base import BaseSoftDeletableDocument
from ...enums import TelegramAudioType


class Playlist(BaseVertex, BaseSoftDeletableDocument):
    _collection_name = "playlists"
    schema_version = 1
    _extra_do_not_update_fields = ("is_favorite",)

    title: str
    description: Optional[str]

    rank: int
    is_favorite: bool = Field(default=False)

    def update_title(
        self,
        title: str,
    ) -> bool:
        """
        Update playlist's title

        Parameters
        ----------
        title : str
            New title for the playlist

        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        if title is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.title = title
        return self.update(self_copy, reserve_non_updatable_fields=False)

    def update_description(
        self,
        description: str,
    ) -> bool:
        """
        Update playlist's description

        Parameters
        ----------
        description : str
            New description for the playlist

        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        if description is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.description = description
        return self.update(self_copy, reserve_non_updatable_fields=False)


class PlaylistMethods:
    _get_user_playlist_by_title_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'],vertexCollections:['@playlists']}"
        "   filter v.is_soft_deleted == not @filter_out and v.title == '@title'"
        "   limit 1"
        "   return v"
    )

    _get_user_playlist_by_key_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'],vertexCollections:['@playlists']}"
        "   filter v.is_soft_deleted == not @filter_out and v._key == '@key'"
        "   limit 1"
        "   return v"
    )

    _get_user_favorite_playlist_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'],vertexCollections:['@playlists']}"
        "   filter v.is_favorite == @is_favorite"
        "   limit 1"
        "   return v"
    )

    _get_user_playlists_query = (
        "for v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'],vertexCollections:['@playlists']}"
        "   sort v.rank ASC, e.created_at DESC"
        "   limit @offset, @limit"
        "   return v"
    )

    _get_playlist_audios_query = (
        "for audio_v,e in 1..1 outbound '@start_vertex' graph '@graph_name' options {order:'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "   sort e.created_at DESC"
        "   limit @offset, @limit"
        "   return audio_v"
    )

    def get_user_playlist_by_title(
        self,
        user: User,
        title: str,
        filter_out_soft_deleted: Optional[bool] = False,
    ) -> Optional[Playlist]:
        """
        Get a `Playlist` with the given `title` if exists, otherwise, return `None`.

        Parameters
        ----------
        user : User
            User with this playlist
        title : str
            Playlist title to check
        filter_out_soft_deleted : Optional[bool]
            Whether to filter out soft-deleted documents in this query

        Returns
        -------
        Playlist, optional
            `Playlist` with the given title if it exists, return `None` otherwise.
        """
        if user is None or title is None:
            return None

        cursor = Playlist.execute_query(
            self._get_user_playlist_by_title_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has._collection_name,
                "playlists": Playlist._collection_name,
                "filter_out": filter_out_soft_deleted,
                "title": title,
            },
        )
        if cursor is not None:
            return Playlist.from_collection(cursor.pop())

        return None

    def get_user_playlist_by_key(
        self,
        user: User,
        key: str,
        filter_out_soft_deleted: Optional[bool] = False,
    ) -> Optional[Playlist]:
        """
        Get a `Playlist` with the given `key` if exists, otherwise, return `None`.

        Parameters
        ----------
        user : User
            User with this playlist
        key : str
            Playlist key to check
        filter_out_soft_deleted : Optional[bool]
            Whether to filter out soft-deleted documents in this query

        Returns
        -------
        Playlist, optional
            `Playlist` with the given title if it exists, return `None` otherwise.
        """
        if user is None or key is None:
            return None

        cursor = Playlist.execute_query(
            self._get_user_playlist_by_key_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has._collection_name,
                "playlists": Playlist._collection_name,
                "filter_out": filter_out_soft_deleted,
                "key": key,
            },
        )
        if cursor is not None:
            return Playlist.from_collection(cursor.pop())

        return None

    def get_user_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        """
        Get a user favorite `Playlist` if exists, otherwise, return `None`.

        Parameters
        ----------
        user : User
            User with this playlist

        Returns
        -------
        Playlist, optional
            Favorite `Playlist` of the `user` if it exists, return `None` otherwise.

        """
        if user is None:
            return None

        cursor = Playlist.execute_query(
            self._get_user_favorite_playlist_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has._collection_name,
                "playlists": Playlist._collection_name,
                "is_favorite": True,
            },
        )
        if cursor is not None:
            return Playlist.from_collection(cursor.pop())
        return None

    def create_playlist(
        self,
        user: User,
        title: str,
        description: str,
        is_favorite: bool,
    ) -> Optional[Playlist]:
        """
        Create a `Playlist` for the given `user` and return it the operation was successful, otherwise, return `None`.

        Parameters
        ----------
        user : User
            User to create the playlist for
        title : str
            Title of the playlist
        description : str, optional
            Description of the playlist
        is_favorite : bool
            Whether the created playlist is favorite or not.

        Returns
        -------
        Playlist, optional
            Favorite `Playlist` of the `user` if it exists, return `None` otherwise.

        Notes
        -----
            Only `1` favorite playlist is allowed per user.
        """

        # making sure of the `key` uniqueness
        while True:
            key = generate_token_urlsafe(10)
            key_exists = Playlist.has(key)
            if key_exists is not None and not key_exists:
                break

        if key is None:
            return None

        v = Playlist(
            key=key,
            title=title,
            description=description,
            is_favorite=is_favorite,
            rank=1 if is_favorite else 2,
        )

        playlist, successful = Playlist.insert(v)

        if playlist and successful:
            try:
                has_edge = Has.get_or_create_edge(user, playlist)
            except ValueError:
                # todo: could not create the has_edge, abort the transaction
                deleted = playlist.delete()
                if not deleted:
                    # todo: could not delete the playlist, what now?
                    logger.error(f"Could not delete playlist: {prettify(playlist)}")
            else:
                return playlist if has_edge else None

        return playlist

    def get_or_create_playlist(
        self,
        user: User,
        title: str,
        description: str = None,
        is_favorite: bool = False,
    ) -> Optional[Playlist]:
        """
        Get a `Playlist` with the given `title` if it exists, otherwise, create it and return it.

        Parameters
        ----------
        user : User
            User to get/create this playlist.
        title : str
            Title of the Playlist
        description : Optional[str]
            Description of the playlist
        is_favorite : bool
            Whether this playlist is favorite or not.

        Returns
        -------
        Playlist, optional
            Created/Retrieved `Playlist` if the operation successful, return `None` otherwise.
        """
        if user is None or title is None:
            return None

        if is_favorite:
            # check if there is a favorite playlist already, one favorite playlist is allowed per user
            user_fav_playlist = self.get_user_favorite_playlist(user)
            if user_fav_playlist:
                # the user has a favorite playlist already
                return user_fav_playlist
        else:
            # non-favorite playlists with reserved names aren't allowed
            # todo: raise an error instead of returning `None`
            if title == "Favorite":
                return None

        # only check the playlists that haven't been soft-deleted.
        playlist = self.get_user_playlist_by_title(user, title, filter_out_soft_deleted=True)
        if playlist:
            return playlist

        return self.create_playlist(user, title, description, is_favorite)

    def create_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        """
        Create a favorite `Playlist` for the given `User` if possible, otherwise, return `None`.

        Parameters
        ----------
        user : User
            User to create the playlist for

        Returns
        -------
        Playlist, optional
            Favorite `Playlist` of the `user` if the operation was successful, return `None` otherwise.

        """
        return self.get_or_create_playlist(
            user,
            title="Favorite",
            description="Favorite Playlist",
            is_favorite=True,
        )

    def get_or_create_favorite_playlist(
        self,
        user: User,
    ) -> Optional[Playlist]:
        """
        Get the favorite `Playlist` of the `User` if it exists, otherwise, Create it and return it.

        Parameters
        ----------
        user : User
            User to get/create the favorite playlist for

        Returns
        -------
        Playlist, optional
            Retrieved/Created `Playlist` for the given `User`, return `None` if the operation wasn't successful.

        """
        playlist = self.get_user_favorite_playlist(user)
        if playlist is None:
            playlist = self.create_favorite_playlist(user)

        return playlist

    def remove_playlist(
        self,
        user: User,
        playlist_key: str,
        deleted_at: int,
    ) -> bool:
        """
        Remove the `Playlist` with the given `playlist_key` and return whether the deletion was successful or not.

        Parameters
        ----------
        user : User
            User that playlist belongs to
        playlist_key : str
            Key of the playlist to delete
        deleted_at : int
            Timestamp of the deletion

        Returns
        -------
        bool
            Whether the deletion operation was successful or not.

        """
        if user is None or playlist_key is None or deleted_at is None:
            return False

        playlist = Playlist.get(playlist_key)
        if not playlist:
            raise KeyError(f"Playlist was not found with key : {playlist_key}")

        # check if the user owns the given playlist
        has_edge: Has = Has.get(Has.parse_key(user, playlist))
        if has_edge:
            try:
                had_edge = Had.get_or_create_edge(user, playlist, has=has_edge, deleted_at=deleted_at)
            except ValueError:
                # fixme: check if the user or playlist are listed in had edge ends.
                pass
            else:
                if had_edge:
                    is_has_deleted = has_edge.delete()
                    is_playlist_deleted = playlist.delete(
                        soft_delete=True,
                        is_exact_date=True,
                        deleted_at=deleted_at,
                    )
                    if is_has_deleted and is_playlist_deleted:
                        return True
                    else:
                        # todo: check which one couldn't be deleted
                        pass
                else:
                    pass
        else:
            pass

        return False

    def get_user_playlists(
        self,
        user: User,
        offset: int = 0,
        limit: int = 10,
    ) -> Generator[Playlist, None, None]:
        """
        Get `User` playlists.

        Parameters
        ----------
        user : User
            User to get playlist list for
        offset : int, default : 0
            Offset to get the playlists query after
        limit : int, default : 10
            Number of `Playlists`s to query

        Yields
        ------
        Playlist
            Playlists that the given user has

        """
        if user is None:
            return None

        cursor = Playlist.execute_query(
            self._get_user_playlists_query,
            bind_vars={
                "start_vertex": user.id,
                "has": Has._collection_name,
                "playlists": Playlist._collection_name,
                "offset": offset,
                "limit": limit,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Playlist.from_collection(doc)

    def _get_playlist_and_audio(
        self: ArangoGraphMethods,
        user: User,
        hit_download_url: str,
        playlist_key: str,
    ) -> Tuple[Playlist, Audio]:
        playlist = self.get_user_playlist_by_key(user, playlist_key, filter_out_soft_deleted=True)
        if playlist is None:
            raise Exception("User does not have playlist with the given `key`")
        hit = self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            raise Exception("No `Hit` exists with the given `download_url`")
        audio = self.get_audio_from_hit(hit)
        if audio is None:
            raise Exception("`Hit` does not have any `Audio` linked to it")
        if audio.audio_type != TelegramAudioType.AUDIO_FILE:
            raise Exception("`Audio` does not have valid audio type for inline mode")
        return playlist, audio

    def add_audio_to_playlist(
        self: ArangoGraphMethods,
        user: User,
        playlist_key: str,
        hit_download_url: str,
    ) -> Tuple[bool, bool]:
        """
        Add `Audio` to the user given `Playlist`

        Parameters
        ----------
        user : User
            User to run the query on
        playlist_key : str
            Playlist key to add the audio to
        hit_download_url : str
            Hit download_url to get the audio from

        Returns
        -------
        tuple
            Whether the operation was successful and added the audio to the user's playlist

        Raises
        ------
        Exception
            If the user does not have a playlist with the given playlist_key, or no hit exists with the given
            hit_download_url, or audio is not valid for inline mode ,or the hit does not have any audio linked to it.

        """
        if user is None or playlist_key is None or hit_download_url is None:
            return False, False

        playlist, audio = self._get_playlist_and_audio(user, hit_download_url, playlist_key)

        has_edge = Has.get(Has.parse_key(playlist, audio))
        if has_edge is not None:
            # Audio is already on the playlist
            return True, False
        else:
            try:
                has_edge = Has.get_or_create_edge(playlist, audio)
            except ValueError:
                logger.error("ValueError: Could not create the `has` from `Playlist` vertex to `Audio` vertex")
                return False, False
            else:
                return True, False

    def remove_audio_from_playlist(
        self: ArangoGraphMethods,
        user: User,
        playlist_key: str,
        hit_download_url: str,
        remove_timestamp: int,
    ) -> Tuple[bool, bool]:
        """
        Remove `Audio` from the user given `Playlist`

        Parameters
        ----------
        user : User
            User to run the query on
        playlist_key : str
            Playlist key to remove the audio from
        hit_download_url : str
            Hit download_url to get the audio from
        remove_timestamp : int
            Timestamp when the removing happened

        Returns
        -------
        tuple
            Whether the operation was successful and removed the audio to the user's playlist

        Raises
        ------
        Exception
            If the user does not have a playlist with the given playlist_key, or no hit exists with the given
            hit_download_url, or audio is not valid for inline mode ,or the hit does not have any audio linked to it, or could not delete the `has` edge.

        """
        if user is None or playlist_key is None or hit_download_url is None:
            return False, False

        playlist, audio = self._get_playlist_and_audio(user, hit_download_url, playlist_key)

        has_edge = Has.get(Has.parse_key(playlist, audio))
        if has_edge is not None:
            # Audio is already on the playlist
            deleted = has_edge.delete()
            if not deleted:
                raise Exception("Could not delete the `has` edge from `Playlist` vertex to `Audio` vertex")

            try:
                had_edge = Had.get_or_create_edge(playlist, audio, has=has_edge, deleted_at=remove_timestamp)
            except ValueError:
                logger.error("ValueError: Could not create the `had` from `Playlist` vertex to `Audio` vertex")
                return False, False
            else:
                return True, True
        else:
            # Audio does not belong to the playlist
            return True, False

    def get_playlist_audios(
        self: ArangoGraphMethods,
        user: User,
        playlist_key: str,
        offset: int = 0,
        limit: int = 10,
    ) -> Generator[Audio, None, None]:
        """
        Get `Playlist` audios.

        Parameters
        ----------
        user : User
            User to get the playlist audios from
        playlist_key : str
            Playlist key to get the audios from
        offset : int, default : 0
            Offset to get the audios query after
        limit : int, default : 10
            Number of `Audio`s to query

        Returns
        -------
        Audio
            Audios that belong to the given playlist

        """
        if user is None:
            return None

        playlist = self.get_user_playlist_by_key(user, playlist_key, filter_out_soft_deleted=True)
        if playlist is None:
            raise Exception("User does not have any `Playlist` with the given `playlist_key`")

        cursor = Audio.execute_query(
            self._get_playlist_audios_query,
            bind_vars={
                "start_vertex": playlist.id,
                "has": Has._collection_name,
                "audios": Audio._collection_name,
                "offset": offset,
                "limit": limit,
            },
        )
        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Audio.from_collection(doc)
