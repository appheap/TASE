from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, BaseVertex


class ArchivedAudio(BaseEdge):
    """
    Connection from `Audio` to the archived `Audio`
    """

    _collection_name = "archived_audio"
    schema_version = 1

    _from_vertex_collections = [Audio]
    _to_vertex_collections = [Audio]

    @classmethod
    def parse_key(
        cls,
        from_vertex: BaseVertex,
        to_vertex: BaseVertex,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: Audio,
        *args,
        **kwargs,
    ) -> Optional["ArchivedAudio"]:
        key = ArchivedAudio.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return ArchivedAudio(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class ArchivedAudioMethods:
    pass
