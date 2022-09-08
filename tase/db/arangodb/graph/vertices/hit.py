from typing import Optional

from tase.db.helpers import SearchMetaData
from tase.utils import generate_token_urlsafe
from .audio import Audio
from .base_vertex import BaseVertex
from .query import Query
from ..edges import Has


class Hit(BaseVertex):
    _collection_name = "hits"
    schema_version = 1

    rank: int
    score: float
    query_date: int

    download_url: Optional[str]

    @classmethod
    def parse_key(
        cls,
        query: Query,
        audio: Audio,
    ) -> Optional[str]:
        if query is None or audio is None:
            return None

        return f"{query.key}:{audio.key}:{query.query_date}"

    @classmethod
    def parse(
        cls,
        query: Query,
        audio: Audio,
        search_metadata: SearchMetaData,
    ) -> Optional["Hit"]:
        if query is None or audio is None:
            return None

        key = Hit.parse_key(query, audio)
        return Hit(
            key=key,
            rank=search_metadata.rank,
            score=search_metadata.score,
            query_date=query.query_date,
            download_url=generate_token_urlsafe(),
        )


class HitMethods:
    def create_hit(
        self,
        query: Query,
        audio: Audio,
        search_metadata: SearchMetaData,
    ) -> Optional[Hit]:
        """
        Create Hit vertex in the ArangoDB.

        Parameters
        ----------
        query : Query
            Query this hit belongs to
        audio : Audio
            Audio this Hit has hit
        search_metadata : SearchMetaData
            Search metadata related to the given Audio returned from ElasticSearch

        Returns
        -------
        Hit, optional
            Hit object if the creation was successful, otherwise, return None

        Raises
        ------
        Exception
            If could not create the `has` edge from `Hit` vertex to `Audio` vertex
        """
        if query is None or audio is None or search_metadata is None:
            return None

        hit, successful = Hit.insert(Hit.parse(query, audio, search_metadata))
        if hit and successful:
            has_audio_edge = Has.get_or_create_edge(hit, audio)
            if has_audio_edge is None:
                raise Exception("Could not create `has` edge from `hit` vertex to `audio` vertex")

            return hit

        return None

    def get_or_create_hit(
        self,
        query: Query,
        audio: Audio,
        search_metadata: SearchMetaData,
    ) -> Optional[Hit]:
        """
        Get Hit if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        query : Query
            Query this hit belongs to
        audio : Audio
            Audio this Hit has hit
        search_metadata : SearchMetaData
            Search metadata related to the given Audio returned from ElasticSearch

        Returns
        -------
        Hit, optional
            Hit object if the operation was successful, otherwise, return None

        Raises
        ------
        Exception
            If could not create the `has` edge from `Hit` vertex to `Audio` vertex
        """
        if query is None or audio is None or search_metadata is None:
            return None

        hit = Hit.get(Hit.parse_key(query, audio))
        if hit is None:
            hit = self.create_hit(query, audio, search_metadata)

        return hit

    def find_by_download_url(
        self,
        download_url: str,
    ) -> Optional["Hit"]:
        if download_url is None:
            return None

        return Hit.find_one({"download_url": download_url})
