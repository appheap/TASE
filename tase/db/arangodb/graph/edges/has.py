from pydantic.typing import Optional, Union, Tuple

from .base_edge import BaseEdge
from ..vertices import User, Playlist, Query, InlineQuery, Hit, Download, Audio, Keyword


class Has(BaseEdge):
    _collection_name = "has"
    schema_version = 1

    _from_vertex_collections = [
        User,
        Playlist,
        Query,
        InlineQuery,
        Hit,
        Download,
    ]
    _to_vertex_collections = [
        Playlist,
        Audio,
        Hit,
        Keyword,
    ]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[User, Playlist, Query, InlineQuery, Hit, Download],
        to_vertex: Union[Playlist, Audio, Hit, Keyword],
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Union[User, Playlist, Query, InlineQuery, Hit, Download],
        to_vertex: Union[Playlist, Audio, Hit, Keyword],
        *args,
        **kwargs,
    ) -> Optional["Has"]:
        key = Has.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return Has(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class HasMethods:
    def create_has_edge(
        self,
        from_vertex: Union[User, Playlist, Query, InlineQuery, Hit, Download],
        to_vertex: Union[Playlist, Audio, Hit, Keyword],
    ) -> Tuple[Optional[Has], bool]:
        if from_vertex is None or to_vertex is None:
            return None, False

        return Has.insert(Has.parse(from_vertex, to_vertex))

    def get_or_create_has_edge(
        self,
        from_vertex: Union[User, Playlist, Query, InlineQuery, Hit, Download],
        to_vertex: Union[Playlist, Audio, Hit, Keyword],
    ) -> Optional[Has]:
        if from_vertex is None or to_vertex is None:
            return None

        has_edge = Has.get(Has.parse_key(from_vertex, to_vertex))
        if not has_edge:
            # has_edge does not exist in the database, create it
            has_edge, successful = self.create_has_edge(from_vertex, to_vertex)

        return has_edge

    def update_or_create_has_edge(
        self,
        from_vertex: Union[User, Playlist, Query, InlineQuery, Hit, Download],
        to_vertex: Union[Playlist, Audio, Hit, Keyword],
    ) -> Optional[Has]:
        if from_vertex is None or to_vertex is None:
            return None

        has_edge = Has.get(Has.parse_key(from_vertex, to_vertex))
        if has_edge is not None:
            # has_edge exists in the database, update it
            has_edge, successful = has_edge.update(Has.parse(from_vertex, to_vertex))
        else:
            # has_edge does not exist in the database, create it
            has_edge, successful = self.create_has_edge(from_vertex, to_vertex)

        return has_edge
