from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Audio, File


class FileRef(BaseEdge):
    """
    Connection from `Audio` to `File`
    """

    _collection_edge_name = "file_ref"

    _from_vertex_collections = [Audio]
    _to_vertex_collections = [File]

    @staticmethod
    def parse_from_audio_and_file(
        audio: Audio,
        file: File,
    ) -> Optional["FileRef"]:
        if audio is None or file is None:
            return None

        key = f"{audio.key}@{file.key}"
        return FileRef(
            key=key,
            from_node=audio,
            to_node=file,
        )
