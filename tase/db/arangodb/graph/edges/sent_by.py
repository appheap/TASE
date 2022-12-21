from __future__ import annotations

from typing import Optional

from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, Chat


class SentBy(BaseEdge):
    """Connection from `Audio` to `Chat`"""

    __collection_name__ = "sent_by"
    schema_version = 1

    __from_vertex_collections__ = (Audio,)
    __to_vertex_collections__ = (Chat,)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional[SentBy]:
        key = SentBy.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return SentBy(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class SentByMethods:
    pass
