from pydantic.typing import Optional, Union

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
    pass
