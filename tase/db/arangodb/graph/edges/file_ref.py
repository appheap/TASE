from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, File


class FileRef(BaseEdge):
    """
    Connection from `Audio` to `File`
    """

    __collection_name__ = "file_ref"
    schema_version = 1

    __from_vertex_collections__ = (Audio,)
    __to_vertex_collections__ = (File,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: File,
        *args,
        **kwargs,
    ) -> Optional[FileRef]:
        key = FileRef.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return FileRef(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class FileRefMethods:
    pass
