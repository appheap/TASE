from __future__ import annotations

import asyncio
import collections
from typing import Optional, TYPE_CHECKING, List, Deque, Set, Union

from aioarango.models import PersistentIndex
from tase.common.utils import generate_token_urlsafe, async_timed
from tase.db.helpers import SearchMetaData
from tase.errors import InvalidFromVertex, InvalidToVertex, EdgeCreationFailed
from tase.my_logger import logger
from ...helpers import HitCount, HitMetadata

if TYPE_CHECKING:
    from .. import ArangoGraphMethods

if TYPE_CHECKING:
    from .audio import Audio
    from .query import Query
    from .playlist import Playlist

from .base_vertex import BaseVertex
from ...enums import HitType


class Hit(BaseVertex):
    __collection_name__ = "hits"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="rank",
            fields=[
                "rank",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="score",
            fields=[
                "score",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="query_date",
            fields=[
                "query_date",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="hit_type",
            fields=[
                "hit_type",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="download_url",
            fields=[
                "download_url",
            ],
            unique=True,
        ),
    ]

    hit_type: HitType
    metadata: Optional[HitMetadata]

    rank: int
    score: float
    query_date: int

    download_url: Optional[str]

    def __getattr__(self, item):
        if item == "metadata":
            return None

        raise AttributeError

    @classmethod
    def parse_key(
        cls,
        query: Query,
        audio_or_playlist: Union[Audio, Playlist],
    ) -> Optional[str]:
        if query is None or audio_or_playlist is None:
            return None

        return f"{query.key}:{audio_or_playlist.key}:{query.query_date}"

    @classmethod
    def parse(
        cls,
        query: Query,
        audio: Audio,
        hit_type: HitType,
        hit_metadata: HitMetadata,
        search_metadata: Optional[SearchMetaData] = None,
        hit_download_url: Optional[str] = None,
    ) -> Optional[Hit]:
        if query is None or audio is None or hit_type is None:
            return None

        key = Hit.parse_key(query, audio)
        return Hit(
            key=key,
            hit_type=hit_type,
            metadata=hit_metadata,
            rank=search_metadata.rank if search_metadata else 0,
            score=search_metadata.score if search_metadata else 0,
            query_date=query.query_date,
            download_url=hit_download_url if hit_download_url else generate_token_urlsafe(),
        )


class HitMethods:
    _count_hits_query = (
        "for hit in @@hits"
        "   filter hit.created_at >= @last_run_at and hit.created_at < @now"
        "   for v,e in 1..1 outbound hit graph @graph_name options {order: 'dfs', edgeCollections:[@has], vertexCollections:[@audios]}"
        "       collect audio_key = v._key, hit_type = hit.hit_type"
        "       aggregate count_ = length(0)"
        "       sort count_ desc, hit_type asc"
        "   return {audio_key, hit_type, count_}"
    )

    @async_timed()
    async def generate_hit_download_urls(
        self,
        size: int = 10,
    ) -> Deque[str]:
        if size <= 0:
            return collections.deque()

        urls: List = await asyncio.gather(
            *(
                asyncio.get_running_loop().run_in_executor(
                    None,
                    generate_token_urlsafe,
                )
                for _ in range(size)
            )
        )
        existence_checks = await asyncio.gather(*(self.find_hit_by_download_url(url) for url in urls))
        for url, existence_check in zip(urls, existence_checks):
            if existence_check:
                urls.remove(url)

        urls: Set = set(urls)
        if len(urls) < size:
            logger.error("duplicate hit urls!")
            for i in range(size - len(urls)):
                while True:
                    url = await asyncio.get_running_loop().run_in_executor(None, generate_token_urlsafe)
                    if url in urls or await self.find_hit_by_download_url(url) or not len(url):
                        continue
                    else:
                        urls.add(url)
                        break

        return collections.deque(urls)

    async def create_hit(
        self: ArangoGraphMethods,
        query: Query,
        audio_or_playlist: Union[Audio, Playlist],
        hit_type: HitType,
        hit_metadata: HitMetadata,
        hit_download_url: str = None,
        search_metadata: Optional[SearchMetaData] = None,
    ) -> Optional[Hit]:
        """
        Create Hit vertex in the ArangoDB.

        Parameters
        ----------
        query : Query
            Query this hit belongs to.
        audio_or_playlist : Audio or Playlist
            Audio or Playlist this Hit has hit.
        hit_type: HitType
            Type of `Hit` vertex.
        hit_metadata : HitMetadata
            Metadata of this hit object.
        hit_download_url : str, default : None
            Hit download URL to initialize the object with.
        search_metadata : SearchMetaData, default : None
            Search metadata related to the given Audio or Playlist returned from ElasticSearch.

        Returns
        -------
        Hit, optional
            Hit object if the creation was successful, otherwise, return None

        Raises
        ------
        EdgeCreationFailed
            If creation of the `has` edge from `Hit` vertex to `Audio` vertex
        """
        if not query or not audio_or_playlist or not hit_type or not hit_metadata:
            return None

        if not hit_download_url:
            while True:
                hit_download_url = await asyncio.get_running_loop().run_in_executor(None, generate_token_urlsafe)

                if not await self.find_hit_by_download_url(hit_download_url):
                    break

        hit = Hit.parse(query, audio_or_playlist, hit_type, hit_metadata, search_metadata, hit_download_url)

        hit, successful = await Hit.insert(hit)
        if hit and successful:
            try:
                from tase.db.arangodb.graph.edges import Has

                has_audio_edge = await Has.get_or_create_edge(hit, audio_or_playlist)
                if has_audio_edge is None:
                    raise EdgeCreationFailed(Has.__class__.__name__)
            except (InvalidFromVertex, InvalidToVertex):
                logger.error(f"ValueError: Could not create `has` edge from `{hit.id}` vertex to `{audio_or_playlist.id}` vertex")

            return hit

        return None

    async def get_or_create_hit(
        self,
        query: Query,
        audio_or_playlist: Union[Audio, Playlist],
        hit_type: HitType,
        hit_metadata: HitMetadata,
        hit_download_url: str = None,
        search_metadata: Optional[SearchMetaData] = None,
    ) -> Optional[Hit]:
        """
        Get Hit if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        query : Query
            Query this hit belongs to.
        audio_or_playlist : Audio or Playlist
            Audio or Playlist this Hit has hit.
        hit_type: HitType
            Type of `Hit` vertex.
        hit_metadata : HitMetadata
            Metadata of this hit object.
        hit_download_url : str, default : None
            Hit download URL to initialize the object with.
        search_metadata : SearchMetaData, default : None
            Search metadata related to the given Audio or Playlist returned from ElasticSearch.

        Returns
        -------
        Hit, optional
            Hit object if the operation was successful, otherwise, return None

        Raises
        ------
        Exception
            If could not create the `has` edge from `Hit` vertex to `Audio` vertex
        """
        if query is None or audio_or_playlist is None or hit_type is None or not hit_metadata:
            return None

        hit = await Hit.get(Hit.parse_key(query, audio_or_playlist))
        if hit is None:
            hit = await self.create_hit(query, audio_or_playlist, hit_type, hit_metadata, hit_download_url, search_metadata)

        return hit

    async def find_hit_by_download_url(
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

        return await Hit.find_one({"download_url": download_url})

    async def count_hits(
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

        res = collections.deque()

        async with await Hit.execute_query(
            self._count_hits_query,
            bind_vars={
                "@hits": Hit.__collection_name__,
                "last_run_at": last_run_at,
                "now": now,
                "has": Has.__collection_name__,
                "audios": Audio.__collection_name__,
            },
        ) as cursor:
            async for doc in cursor:
                obj = HitCount.parse(doc)
                if obj is not None:
                    res.append(obj)

        return list(res)
