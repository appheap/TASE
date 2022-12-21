from __future__ import annotations

from typing import Optional, Union

from aioarango.models import PersistentIndex
from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, Playlist, Query, Hashtag
from ...enums import MentionSource


class HasHashtag(BaseEdge):
    __collection_name__ = "has_hashtag"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="is_direct_mention",
            fields=[
                "is_direct_mention",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="mention_source",
            fields=[
                "mention_source",
            ],
        ),
    ]

    __from_vertex_collections__ = (
        Audio,
        Playlist,
        Query,
    )
    __to_vertex_collections__ = (Hashtag,)

    is_direct_mention: bool
    mention_source: MentionSource
    mention_start_index: int

    @classmethod
    def parse_has_hashtag_key(
        cls,
        from_vertex_key: str,
        to_vertex_key: str,
        mention_source: MentionSource,
        mention_start_index: int,
    ) -> Optional[str]:
        if not from_vertex_key or not to_vertex_key or not mention_source or mention_start_index is None:
            return None

        return f"{from_vertex_key}:{to_vertex_key}:{mention_source.value}:{mention_start_index}"

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

        return cls.parse_has_hashtag_key(from_vertex.key, to_vertex.key, mention_source, mention_start_index)

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
