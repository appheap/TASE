from pydantic.typing import Optional, Union

from .base_edge import BaseEdge
from .has import Has
from ..vertices import (
    Audio,
    Playlist,
    User,
)


class Had(BaseEdge):
    _collection_name = "had"
    schema_version = 1

    deleted_at: int
    metadata_created_at: int
    metadata_modified_at: int

    _from_vertex_collections = [
        User,
        Playlist,
    ]
    _to_vertex_collections = [
        Playlist,
        Audio,
    ]

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[User, Playlist],
        to_vertex: Union[Playlist, Audio],
        deleted_at: int,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None or deleted_at is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}:{deleted_at}"

    @classmethod
    def parse(
        cls,
        from_vertex: Union[User, Playlist],
        to_vertex: Union[User, Playlist],
        deleted_at: int,
        has: Has,
        *args,
        **kwargs,
    ) -> Optional["Had"]:
        key = Had.parse_key(from_vertex, to_vertex, deleted_at)
        if key is None:
            return None

        if has is None:
            return None

        return Had(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
            deleted_at=deleted_at,
            metadata_created_at=has.created_at,
            metadata_modified_at=has.modified_at,
        )


class HadMethods:
    pass
