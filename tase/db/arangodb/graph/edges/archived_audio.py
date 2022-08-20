from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio


class ArchivedAudio(BaseEdge):
    """
    Connection from `Audio` to the archived `Audio`
    """

    _collection_name = "archived_audio"
    schema_version = 1

    _from_vertex_collections = (Audio,)
    _to_vertex_collections = (Audio,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: Audio,
        *args,
        **kwargs,
    ) -> Optional["ArchivedAudio"]:
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
