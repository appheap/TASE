from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio


class ArchivedAudio(BaseEdge):
    """
    Connection from `Audio` to the archived `Audio`
    """

    __collection_name__ = "archived_audio"
    schema_version = 1

    __from_vertex_collections__ = (Audio,)
    __to_vertex_collections__ = (Audio,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: Audio,
        *args,
        **kwargs,
    ) -> Optional[ArchivedAudio]:
        key = ArchivedAudio.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return ArchivedAudio(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class ArchivedAudioMethods:
    pass
