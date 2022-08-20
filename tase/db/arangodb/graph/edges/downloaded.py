from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Download, User


class Downloaded(BaseEdge):
    """
    Connection from `User` to `Download`
    """

    _collection_name = "downloaded"
    schema_version = 1

    _from_vertex_collections = (User,)
    _to_vertex_collections = (Download,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: User,
        to_vertex: Download,
        *args,
        **kwargs,
    ) -> Optional["Downloaded"]:
        key = Downloaded.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return Downloaded(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class DownloadedMethods:
    pass
