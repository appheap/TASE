from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from tase.db.helpers import SearchMetaData
from tase.errors import InvalidFromVertex, InvalidToVertex, EdgeCreationFailed
from tase.my_logger import logger
from tase.utils import generate_token_urlsafe

if TYPE_CHECKING:
    from .. import ArangoGraphMethods

if TYPE_CHECKING:
    from .audio import Audio
    from .query import Query
from .base_vertex import BaseVertex
from ...enums import HitType


class Hit(BaseVertex):
    _collection_name = "hits"
    schema_version = 1

    hit_type: HitType

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
        hit_type: HitType,
        search_metadata: Optional[SearchMetaData] = None,
    ) -> Optional[Hit]:
        if query is None or audio is None or hit_type is None:
            return None

        key = Hit.parse_key(query, audio)
        return Hit(
            key=key,
            hit_type=hit_type,
            rank=search_metadata.rank if search_metadata else 0,
            score=search_metadata.score if search_metadata else 0,
            query_date=query.query_date,
            download_url=generate_token_urlsafe(),
        )


class HitMethods:
    def create_hit(
        self: ArangoGraphMethods,
        query: Query,
        audio: Audio,
        hit_type: HitType,
        search_metadata: Optional[SearchMetaData] = None,
    ) -> Optional[Hit]:
        """
        Create Hit vertex in the ArangoDB.

        Parameters
        ----------
        query : Query
            Query this hit belongs to
        audio : Audio
            Audio this Hit has hit
        hit_type: HitType
            Type of `Hit` vertex
        search_metadata : SearchMetaData, default : None
            Search metadata related to the given Audio returned from ElasticSearch

        Returns
        -------
        Hit, optional
            Hit object if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation o the `has` edge from `Hit` vertex to `Audio` vertex
        """
        if query is None or audio is None or hit_type is None:
            return None

        hit = Hit.parse(query, audio, hit_type, search_metadata)
        while True:
            if not self.find_hit_by_download_url(hit.download_url):
                break

            hit.download_url = generate_token_urlsafe()

        hit, successful = Hit.insert(hit)
        if hit and successful:
            try:
                from tase.db.arangodb.graph.edges import Has

                has_audio_edge = Has.get_or_create_edge(hit, audio)
                if has_audio_edge is None:
                    raise EdgeCreationFailed(Has.__class__.__name__)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error(
                    "ValueError: Could not create `has` edge from `hit` vertex to `audio` vertex"
                )

            return hit

        return None

    def get_or_create_hit(
        self,
        query: Query,
        audio: Audio,
        hit_type: HitType,
        search_metadata: Optional[SearchMetaData] = None,
    ) -> Optional[Hit]:
        """
        Get Hit if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        query : Query
            Query this hit belongs to
        audio : Audio
            Audio this Hit has hit
        hit_type: HitType
            Type of `Hit` vertex
        search_metadata : SearchMetaData, default : None
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
        if query is None or audio is None or hit_type is None:
            return None

        hit = Hit.get(Hit.parse_key(query, audio))
        if hit is None:
            hit = self.create_hit(query, audio, hit_type, search_metadata)

        return hit

    def find_hit_by_download_url(
        self,
        download_url: str,
    ) -> Optional[Hit]:
        """
        Get `Hit` by its `download_url`.

        Parameters
        ----------
        download_url : str
            Download URL of the `Hit` vertex

        Returns
        -------
        Hit, optional
            Hit vertex if found in the ArangoDB, otherwise, return None

        """
        if download_url is None:
            return None

        return Hit.find_one({"download_url": download_url})
