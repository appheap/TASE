from __future__ import annotations

import collections
from itertools import chain
from typing import Optional, List, Tuple, Deque

from elastic_transport import ObjectApiResponse
from pydantic import Field

from tase.common.preprocessing import remove_hashtags, is_non_digit, is_non_space
from tase.common.utils import async_timed, find_unique_hashtag_strings
from tase.db.arangodb import graph as graph_models
from tase.errors import PlaylistDoesNotExists
from tase.my_logger import logger
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
            "playlist_downloads": {"type": "long"},
            "audio_downloads": {"type": "long"},
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
    playlist_downloads: int = Field(default=0)
    audio_downloads: int = Field(default=0)

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

        hashtags = list(set(chain(find_unique_hashtag_strings(self.title), find_unique_hashtag_strings(self.description))))
        if hashtags:
            self_copy.hashtags = hashtags

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

        hashtags = list(set(chain(find_unique_hashtag_strings(self.title), find_unique_hashtag_strings(self.description))))
        if hashtags:
            self_copy.hashtags = hashtags

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
        has_query = False

        hashtags_lst = find_unique_hashtag_strings(query)
        if hashtags_lst:
            filter_ = [
                {"term": {"is_soft_deleted": False}},
                {"terms": {"hashtags": hashtags_lst}},
            ]
            query = remove_hashtags(query)
            if query:
                query = query.strip()
                if query and is_non_digit(query) and is_non_space(query):
                    has_query = True

        else:
            filter_ = [
                {"term": {"is_soft_deleted": False}},
            ]

        if has_query:
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
                    "filter": filter_,
                }
            }
        else:
            return {
                "bool": {
                    "filter": filter_,
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
        if not v:
            return None

        hashtags = list(set(chain(find_unique_hashtag_strings(title), find_unique_hashtag_strings(description))))
        if hashtags:
            v.hashtags = hashtags

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
        if from_ is None or not size:
            return None, None

        playlists, query_metadata = await Playlist.search(
            query,
            from_,
            size,
        )
        return playlists, query_metadata

    async def get_top_playlists(
        self,
        from_: int = 0,
        size: int = 10,
    ) -> Tuple[Optional[Deque[Playlist]], Optional[ElasticQueryMetadata]]:
        """
        Search among the documents with the given query

        Parameters
        ----------
        from_ : int, default : 0
            Number of documents to skip in the query
        size : int, default : 10
            Number of documents to return


        Returns
        -------
        tuple
            List of documents matching the query alongside the query metadata

        """

        db_docs = collections.deque()
        try:
            res: ObjectApiResponse = await Playlist.__es__.search(
                index=Playlist.__index_name__,
                from_=from_,
                size=size,
                track_total_hits=False,
                query={
                    "bool": {
                        "filter": [
                            {"term": {"is_soft_deleted": False}},
                        ],
                    }
                },
                sort=Playlist.get_sort(),
            )

            hits = res.body["hits"]["hits"]

            duration = res.meta.duration
            try:
                total_hits = res.body["hits"]["total"]["value"] or 0
            except KeyError:
                total_hits = None
            try:
                total_rel = res.body["hits"]["total"]["relation"]
            except KeyError:
                total_rel = None
            max_score = res.body["hits"]["max_score"] or 0

            query_metadata = {
                "duration": duration,
                "total_hits": total_hits,
                "total_rel": total_rel,
                "max_score": max_score,
            }

            query_metadata = ElasticQueryMetadata.parse(query_metadata)

            for index, hit in enumerate(hits, start=1):
                try:
                    db_doc = Playlist.from_index(
                        hit=hit,
                        rank=index,
                    )
                except ValueError:
                    # fixme: happens when the `hit` is None
                    pass
                else:
                    db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        else:
            return db_docs, query_metadata

        return None, None

    async def get_playlist_by_id(
        self,
        id: str,
    ) -> Optional[Playlist]:
        """
        Get `Playlist` by its `ID`

        Parameters
        ----------
        id : str
            ID of the `Playlist` to get

        Returns
        -------
        Playlist, optional
            Playlist if it exists in ElasticSearch, otherwise, return None

        """
        return await Playlist.get(id)
