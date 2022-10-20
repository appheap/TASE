from __future__ import annotations

from typing import Optional, Union

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import (
    User,
    Playlist,
    Query,
    Hit,
    Interaction,
    Audio,
    Keyword,
    Username,
    Chat,
)


class Has(BaseEdge):
    _collection_name = "has"
    schema_version = 1

    _from_vertex_collections = (
        User,
        Playlist,
        Query,
        Hit,
        Interaction,
        Audio,
        Chat,
    )
    _to_vertex_collections = (
        Playlist,
        Audio,
        Hit,
        Keyword,
        Interaction,
        Username,
    )

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Union[User, Playlist, Query, Hit, Interaction, Audio, Username],
        to_vertex: Union[Playlist, Audio, Hit, Keyword, Interaction, Chat],
        *args,
        **kwargs,
    ) -> Optional[Has]:
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
