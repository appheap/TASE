from __future__ import annotations

import collections
from typing import Optional, TYPE_CHECKING, List

from tase.common.utils import generate_token_urlsafe
from tase.db.helpers import SearchMetaData
from tase.errors import InvalidFromVertex, InvalidToVertex, EdgeCreationFailed
from tase.my_logger import logger
from ...helpers import HitCount

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
    _count_hits_query = (
        "for hit in @hits"
        "   filter hit.created_at >= @last_run_at and hit.created_at < @now"
        "   for v,e in 1..1 outbound hit graph '@graph_name' options {order: 'dfs', edgeCollections:['@has'], vertexCollections:['@audios']}"
        "       collect audio_key = v._key, hit_type = hit.hit_type"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, hit_type asc"
        "   return {audio_key, hit_type, count_}"
    )

    def generate_hit_download_urls(
        self,
        count: int = 10,
    ) -> List[str]:
        hits = collections.deque()
        for i in range(count):
            while True:
                url = generate_token_urlsafe()
                if url in hits or self.find_hit_by_download_url(url) or not len(url):
                    continue
                else:
                    hits.append(url)
                    break

        return list(hits)

    def create_hit(
        self: ArangoGraphMethods,
        query: Query,
        audio: Audio,
        hit_type: HitType,
        hit_download_url: str = None,
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
        hit_download_url : str, default : None
            Hit download URL to initialize the object with
        search_metadata : SearchMetaData, default : None
            Search metadata related to the given Audio returned from ElasticSearch

        Returns
        -------
        Hit, optional
            Hit object if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the `has` edge from `Hit` vertex to `Audio` vertex
        """
        if query is None or audio is None or hit_type is None:
            return None

        hit = Hit.parse(query, audio, hit_type, search_metadata)
        if hit_download_url is None or not len(hit_download_url):
            while True:
                if not self.find_hit_by_download_url(hit.download_url):
                    break

                hit.download_url = generate_token_urlsafe()
        else:
            hit.download_url = hit_download_url

        hit, successful = Hit.insert(hit)
        if hit and successful:
            try:
                from tase.db.arangodb.graph.edges import Has

                has_audio_edge = Has.get_or_create_edge(hit, audio)
                if has_audio_edge is None:
                    raise EdgeCreationFailed(Has.__class__.__name__)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error("ValueError: Could not create `has` edge from `hit` vertex to `audio` vertex")

            return hit

        return None

    def get_or_create_hit(
        self,
        query: Query,
        audio: Audio,
        hit_type: HitType,
        hit_download_url: str = None,
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
        hit_download_url : str, default : None
            Hit download URL to initialize the object with
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
            hit = self.create_hit(query, audio, hit_type, hit_download_url, search_metadata)

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

    def count_hits(
        self,
        last_run_at: int,
        now: int,
    ) -> List[HitCount]:
        """
        Count the `Hit` vertices that have been created in the ArangoDB between `now` and `last_run_at` parameters.

        Parameters
        ----------
        last_run_at : int
            Timestamp of last run
        now : int
            Timestamp of now

        Returns
        -------
        list of HitCount
            List of HitCount objects

        """
        if last_run_at is None:
            return []

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.vertices import Audio

        cursor = Hit.execute_query(
            self._count_hits_query,
            bind_vars={
                "hits": Hit._collection_name,
                "last_run_at": last_run_at,
                "now": now,
                "has": Has._collection_name,
                "audios": Audio._collection_name,
            },
        )

        res = collections.deque()
        if cursor is not None and len(cursor):
            for doc in cursor:
                obj = HitCount.parse(doc)
                if obj is not None:
                    res.append(obj)

        return list(res)
