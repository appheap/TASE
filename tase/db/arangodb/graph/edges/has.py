from __future__ import annotations

from typing import Optional, Union

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import (
    User,
    Playlist,
    Query,
    Hit,
    AudioInteraction,
    Audio,
    Keyword,
    Username,
    Chat,
    PlaylistInteraction,
    Thumbnail,
    ThumbnailFile,
)


class Has(BaseEdge):
    __collection_name__ = "has"
    schema_version = 1

    __from_vertex_collections__ = (
        User,
        Playlist,
        Query,
        Hit,
        AudioInteraction,
        PlaylistInteraction,
        Audio,
        Chat,
        Thumbnail,
    )
    __to_vertex_collections__ = (
        Playlist,
        Audio,
        PlaylistInteraction,
        Hit,
        Keyword,
        AudioInteraction,
        Username,
        Thumbnail,
        ThumbnailFile,
    )

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Union[User, Playlist, Query, Hit, AudioInteraction, PlaylistInteraction, Audio, Username, Thumbnail],
        to_vertex: Union[Playlist, Audio, Hit, Keyword, AudioInteraction, PlaylistInteraction, Chat, ThumbnailFile],
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
