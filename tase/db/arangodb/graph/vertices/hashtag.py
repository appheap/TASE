from __future__ import annotations

import collections
from hashlib import sha1
from typing import Optional, List, Tuple, TYPE_CHECKING

from aioarango.models import PersistentIndex
from .base_vertex import BaseVertex

if TYPE_CHECKING:
    from ..edges import HasHashtag


class Hashtag(BaseVertex):
    schema_version = 1
    __collection_name__ = "hashtags"
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="hashtag",
            fields=[
                "hashtag",
            ],
        ),
    ]

    hashtag: str

    @classmethod
    def parse_key(
        cls,
        hashtag: str,
    ) -> Optional[str]:
        if hashtag is None or not len(hashtag):
            return None

        res = hashtag.split("#")
        if not len(res) == 2:
            return None

        return f"{sha1(res[1].encode('utf-8')).hexdigest()}"

    @classmethod
    def parse(
        cls,
        hashtag: str,
    ) -> Optional[Hashtag]:
        key = cls.parse_key(hashtag)
        if key is None:
            return None

        return Hashtag(
            key=key,
            hashtag=hashtag.split("#")[1],
        )


class HashTagMethods:
    _get_audio_hashtags_with_edge_query = (
        "for v, e in 1..1 outbound @audio_vertex graph @graph_name options {order: 'dfs', edgeCollections: [@has_hashtag], vertexCollections: [@hashtags]}"
        "   sort e.created_at asc"
        "   return {vertex: v, edge: e}"
    )

    async def create_hashtag(
        self,
        hashtag: str,
    ) -> Optional[Hashtag]:
        """
        Create `Hashtag` vertex in the ArangoDB.

        Parameters
        ----------
        hashtag : str
            Hashtag string to create the vertex from

        Returns
        -------
        Hashtag, optional
            Hashtag if the creation was successful, otherwise, return None

        """
        if hashtag is None:
            return None

        hashtag_vertex, successful = await Hashtag.insert(Hashtag.parse(hashtag))
        if hashtag_vertex and successful:
            return hashtag_vertex

        return None

    async def get_or_create_hashtag(
        self,
        hashtag: str,
    ) -> Optional[Hashtag]:
        """
        Get `Hashtag` vertex if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        hashtag : str
            Hashtag string to get/create the vertex from

        Returns
        -------
        Hashtag, optional
            Hashtag if the operation was successful, otherwise, return None

        """
        if hashtag is None:
            return None

        hashtag_vertex = await Hashtag.get(Hashtag.parse_key(hashtag))
        if hashtag_vertex is None:
            hashtag_vertex = await self.create_hashtag(hashtag)

        return hashtag_vertex

    async def update_or_create_hashtag(
        self,
        hashtag: str,
    ) -> Optional[Hashtag]:
        """
        Update `Hashtag` vertex if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        hashtag : str
            Hashtag string to update/create the vertex from

        Returns
        -------
        Hashtag, optional
            Hashtag if the operation was successful, otherwise, return None

        """
        if hashtag is None:
            return None

        hashtag_vertex = await Hashtag.get(Hashtag.parse_key(hashtag))
        if hashtag_vertex is None:
            hashtag_vertex = await self.create_hashtag(hashtag)
        else:
            await hashtag_vertex.update(Hashtag.parse(hashtag))

        return hashtag_vertex

    async def get_audio_hashtags_with_edges(
        self,
        audio_vertex_id: str,
    ) -> List[Tuple[Hashtag, HasHashtag]]:
        """
        Get `hashtag` vertices belonging to an `audio` vertex along with edges.

        Parameters
        ----------
        audio_vertex_id : str
            ID of the audio vertex.

        Returns
        -------
        list
            List of tuple of `hashtag` vertices and `has_hashtag` edges.
        """
        if not audio_vertex_id:
            return []

        from ..edges import HasHashtag

        res = collections.deque()
        async with await Hashtag.execute_query(
            self._get_audio_hashtags_with_edge_query,
            bind_vars={
                "audio_vertex": audio_vertex_id,
                "has_hashtag": HasHashtag.__collection_name__,
                "hashtags": Hashtag.__collection_name__,
            },
        ) as cursor:
            async for d in cursor:
                if "vertex" in d and "edge" in d:
                    res.append(
                        (
                            Hashtag.from_collection(d["vertex"]),
                            HasHashtag.from_collection(d["edge"]),
                        )
                    )

        return list(res)
