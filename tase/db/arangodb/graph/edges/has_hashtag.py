from __future__ import annotations

from typing import Optional, Union

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, Playlist, Query, Hashtag
from ...enums import MentionSource


class HasHashtag(BaseEdge):
    _collection_name = "has_hashtag"
    schema_version = 1

    _from_vertex_collections = (
        Audio,
        Playlist,
        Query,
    )
    _to_vertex_collections = (Hashtag,)

    is_direct_mention: bool
    mention_source: MentionSource
    mention_start_index: int

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[Audio, Playlist, Query],
        to_vertex: Hashtag,
        mention_source: MentionSource,
        mention_start_index: int,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None or mention_source is None or mention_start_index is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}:{mention_source.value}:{mention_start_index}"

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Union[Audio, Playlist, Query],
        to_vertex: Hashtag,
        mention_source: MentionSource,
        mention_start_index: int,
    ) -> Optional[HasHashtag]:
        key = HasHashtag.parse_key(
            from_vertex,
            to_vertex,
            mention_source,
            mention_start_index,
        )
        if key is None:
            return None

        return HasHashtag(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
            is_direct_mention=MentionSource.is_direct_mention(mention_source),
            mention_source=mention_source,
            mention_start_index=mention_start_index,
        )


class HasHashtagMethods:
    pass
