from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, File


class FileRef(BaseEdge):
    """
    Connection from `Audio` to `File`
    """

    _collection_name = "file_ref"
    schema_version = 1

    _from_vertex_collections = [Audio]
    _to_vertex_collections = [File]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Audio,
        to_vertex: File,
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
        to_vertex: File,
        *args,
        **kwargs,
    ) -> Optional["FileRef"]:
        key = FileRef.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return FileRef(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class FileRefMethods:
    pass
