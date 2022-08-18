from pydantic.typing import Optional, Union

from .base_edge import BaseEdge
from ..vertices import User, Playlist, Query, InlineQuery, Hit, Download, Audio, Keyword


class Has(BaseEdge):
    _collection_name = "has"
    schema_version = 1

    _from_vertex_collections = (
        User,
        Playlist,
        Query,
        InlineQuery,
        Hit,
        Download,
    )
    _to_vertex_collections = (
        Playlist,
        Audio,
        Hit,
        Keyword,
    )

    @classmethod
    def parse(
        cls,
        from_vertex: Union[User, Playlist, Query, InlineQuery, Hit, Download],
        to_vertex: Union[Playlist, Audio, Hit, Keyword],
        *args,
        **kwargs,
    ) -> Optional["Has"]:
        key = Has.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return Has(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class HasMethods:
    pass