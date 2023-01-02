from __future__ import annotations

import collections
from hashlib import sha1
from typing import Optional, List, Tuple, TYPE_CHECKING, Union

from aioarango.models import PersistentIndex
from tase.errors import EdgeCreationFailed
from tase.my_logger import logger
from .base_vertex import BaseVertex
from ...enums import MentionSource

if TYPE_CHECKING:
    from ..edges import HasHashtag
    from . import Audio, Playlist, Query
    from .. import ArangoGraphMethods


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
    _get_vertex_hashtags_with_edge_query = (
        "for v, e in 1..1 outbound @vertex_id graph @graph_name options {order: 'dfs', edgeCollections: [@has_hashtag], vertexCollections: [@hashtags]}"
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

    async def update_connected_hashtags(
        self: ArangoGraphMethods,
        source_vertex: Union[Audio, Playlist, Query],
        hashtags: List[Tuple[str, int, MentionSource]],
    ) -> None:
        """
        Update connected `hashtag` vertices and edges connected to and `Audio` vertex after being updated.

        Parameters
        ----------
        source_vertex : Audio or Playlist or Query
            Vertex to update its `hashtag` edges.
        hashtags : list
            The new hashtags to update the edges by.

        Raises
        ------
        EdgeCreationFailed
            If creation of the related edges was unsuccessful.
        """
        from tase.db.arangodb.graph.edges import HasHashtag
        from . import Audio, Playlist, Query

        if not source_vertex or not isinstance(source_vertex, (Audio, Playlist, Query)):
            # wrong source vertex type
            return

        # get the current hashtag vertices and edges connected to this vertex
        current_hashtags_and_edges_list = await self.get_vertex_hashtags_with_edges(source_vertex.id)
        current_vertices = {hashtag.key for hashtag, _ in current_hashtags_and_edges_list}
        current_edges = {edge.key for _, edge, in current_hashtags_and_edges_list}

        current_vertices_mapping = {hashtag.key: hashtag for hashtag, _ in current_hashtags_and_edges_list}
        current_edges_mapping = {edge.key: edge for _, edge, in current_hashtags_and_edges_list}

        # find the new hashtag vertices and edges keys
        new_vertices = set()
        new_edges = set()

        new_vertices_mapping = dict()
        new_edges_mapping = dict()

        for hashtag_string, start_index, mention_source in hashtags:
            hashtag_key = Hashtag.parse_key(hashtag_string)
            edge_key = HasHashtag.parse_has_hashtag_key(source_vertex.key, hashtag_key, mention_source, start_index)

            new_vertices.add(hashtag_key)
            new_edges.add(edge_key)

            new_vertices_mapping[hashtag_key] = hashtag_string
            new_edges_mapping[edge_key] = (hashtag_key, start_index, mention_source)

        # find the difference between the current and new state of vertices and edges
        removed_vertices = current_vertices - new_vertices  # since a hashtag vertex might be connected to other vertices, it's best not to delete it.
        removed_edges = current_edges - new_edges

        to_create_vertices = new_vertices - current_vertices
        to_create_edges = new_edges - current_edges

        # delete the removed edges
        for edge_key in removed_edges:
            to_be_removed_edge: HasHashtag = current_edges_mapping[edge_key]
            if not await to_be_removed_edge.delete():
                logger.error(f"Error in deleting `HasHashtag` edge with key `{to_be_removed_edge.key}`")

        # create new hashtag vertices
        for hashtag_key in to_create_vertices:
            hashtag_string: str = new_vertices_mapping.get(hashtag_key, None)
            if hashtag_string:
                _vertex = await self.get_or_create_hashtag(hashtag_string)
                if _vertex:
                    current_vertices_mapping[hashtag_key] = _vertex

        # create the new edges
        for edge_key in to_create_edges:
            hashtag_key, start_index, mention_source = new_edges_mapping[edge_key]
            hashtag_vertex = current_vertices_mapping.get(hashtag_key, None)
            if hashtag_vertex:
                has_hashtag = await HasHashtag.get_or_create_edge(
                    source_vertex,
                    hashtag_vertex,
                    mention_source,
                    start_index,
                )
                if has_hashtag is None:
                    raise EdgeCreationFailed(HasHashtag.__class__.__name__)

    async def get_vertex_hashtags_with_edges(
        self,
        vertex_id: str,
    ) -> List[Tuple[Hashtag, HasHashtag]]:
        """
        Get `hashtag` vertices belonging to a vertex along with edges.

        Parameters
        ----------
        vertex_id : str
            ID of the audio vertex.

        Returns
        -------
        list
            List of tuple of `hashtag` vertices and `has_hashtag` edges.
        """
        if not vertex_id:
            return []

        from ..edges import HasHashtag

        res = collections.deque()
        async with await Hashtag.execute_query(
            self._get_vertex_hashtags_with_edge_query,
            bind_vars={
                "vertex_id": vertex_id,
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
