from __future__ import annotations

from typing import Optional, List, Tuple, Deque

from pydantic import Field

from tase.common.utils import async_timed
from tase.db.arangodb import graph as graph_models
from tase.errors import PlaylistDoesNotExists
from .base_document import BaseDocument
from ...arangodb.base import BaseSoftDeletableDocument
from ...arangodb.helpers import ElasticQueryMetadata


class Playlist(BaseDocument, BaseSoftDeletableDocument):
    schema_version = 1

    __index_name__ = "playlists_index"
    __mappings__ = {
        "properties": {
            "schema_version": {"type": "integer"},
            "created_at": {"type": "long"},
            "modified_at": {"type": "long"},
            "owner_user_id": {"type": "long"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "subscribers": {"type": "long"},
            "shares": {"type": "long"},
            ####################################
            "is_soft_deleted": {"type": "boolean"},
            "soft_deleted_at": {"type": "long"},
            "is_soft_deleted_time_precise": {"type": "boolean"},
        }
    }

    __non_updatable_fields__ = (
        "subscribers",
        "shares",
    )
    __search_fields__ = [
        "title",
        "description",
    ]

    owner_user_id: int
    title: str
    description: Optional[str]
    hashtags: List[str] = Field(default_factory=list)

    subscribers: int = Field(default=1)
    shares: int = Field(default=0)

    async def update_title(
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
        return await self.update(self_copy, reserve_non_updatable_fields=False)

    async def update_description(
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
        return await self.update(self_copy, reserve_non_updatable_fields=False)

    async def update_last_modified_date(self):
        """
        Update last modified date field of the playlist.

        Notes
        -----
        This method is called when a new audio has been added to this playlist. It is done to place the last recently used playlist on top.

        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        return await self.update(
            self.copy(deep=True),
            reserve_non_updatable_fields=True,
        )

    @classmethod
    def get_query(
        cls,
        query: Optional[str],
        filter_by_valid_for_inline_search: Optional[bool] = True,
    ) -> Optional[dict]:
        return {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fuzziness": "AUTO",
                        "type": "best_fields",
                        "minimum_should_match": "75%",
                        "fields": cls.__search_fields__,
                    }
                },
                "filter": [
                    {"term": {"is_soft_deleted": False}},
                ],
            }
        }

    @classmethod
    def get_sort(
        cls,
    ) -> Optional[dict]:
        return {
            "_score": {"order": "desc"},
            "subscribers": {"order": "desc"},
            "shares": {"order": "desc"},
        }


class PlaylistMethods:
    async def create_playlist(
        self,
        user: graph_models.vertices.User,
        key: str,
        title: str,
        description: str,
    ) -> Optional[Playlist]:
        """
        Create a `Playlist` for the given `user` and return it the operation was successful, otherwise, return `None`.

        Parameters
        ----------
        user : User
            User to create the playlist for
        key : str
            Key of the playlist.
        title : str
            Title of the playlist
        description : str, optional
            Description of the playlist

        Returns
        -------
        Playlist, optional
            Created `Playlist` if operation is successful, otherwise, return `None`.
        """

        if not key or not title or not user:
            return None

        v = Playlist(
            id=key,
            owner_user_id=user.user_id,
            title=title,
            description=description,
        )

        playlist, successful = await Playlist.create(v)

        if playlist and successful:
            return playlist

        return None

    async def get_or_create_playlist(
        self,
        user: graph_models.vertices.User,
        key: str,
        title: str,
        description: str = None,
    ) -> Optional[Playlist]:
        """
        Get a `Playlist` with the given `title` if it exists, otherwise, create it and return it.

        Parameters
        ----------
        user : User
            User to get/create this playlist.
        key : str
            Key of the playlist.
        title : str
            Title of the Playlist
        description : str, default : None
            Description of the playlist

        Returns
        -------
        Playlist, optional
            Created/Retrieved `Playlist` if the operation successful, return `None` otherwise.
        """
        if user is None or title is None:
            return None

        playlist = await Playlist.get(key)
        if playlist:
            return playlist

        return await self.create_playlist(user, key, title, description)

    async def remove_playlist(
        self,
        user: graph_models.vertices.User,
        playlist_key: str,
        deleted_at: int,
    ) -> bool:
        """
        Remove the `Playlist` with the given `playlist_key` and return whether the deletion was successful or not.

        Parameters
        ----------
        user : graph_models.vertices.User
            User that playlist belongs to
        playlist_key : str
            Key of the playlist to delete
        deleted_at : int
            Timestamp of the deletion

        Raises
        ------
        PlaylistDoesNotExists
            If the user does not have a playlist with the given `playlist_key` parameter

        Returns
        -------
        bool
            Whether the deletion operation was successful or not.

        """
        if user is None or playlist_key is None or deleted_at is None:
            return False

        playlist = await Playlist.get(playlist_key)
        if not playlist:
            raise PlaylistDoesNotExists(user.key, playlist_key)

        return await playlist.delete(
            soft_delete=True,
            is_exact_date=True,
            deleted_at=deleted_at,
        )

    @async_timed()
    async def search_playlists(
        self,
        query: str,
        from_: int = 0,
        size: int = 10,
    ) -> Tuple[Optional[Deque[Playlist]], Optional[ElasticQueryMetadata]]:
        """
        Search among the playlist items with the given query.

        Parameters
        ----------
        query : str
            Query string to search for
        from_ : int, default : 0
            Number of playlist items to skip in the query
        size : int, default : 50
            Number of audio files to return


        Returns
        -------
        tuple
            List of playlist items matching the query alongside the query metadata.

        """
        if query is None or not len(query) or from_ is None or size is None:
            return None, None

        playlists, query_metadata = await Playlist.search(
            query,
            from_,
            size,
        )
        return playlists, query_metadata
