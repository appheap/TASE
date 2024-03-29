from __future__ import annotations

from typing import Optional, Union

from aioarango.models import PersistentIndex
from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import Audio, Chat, User


class ForwardedFrom(BaseEdge):
    """Connection from `Audio` to a `Chat` or an `Audio`"""

    __collection_name__ = "forwarded_from"
    schema_version = 1
    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="date",
            fields=[
                "date",
            ],
        ),
    ]

    __from_vertex_collections__ = (Audio,)
    __to_vertex_collections__ = (User, Chat, Audio)

    signature: Optional[str]
    from_message_id: Optional[int]
    date: Optional[int]

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Audio,
        to_vertex: Union[Chat, Audio],
        *args,
        **kwargs,
    ) -> Optional[ForwardedFrom]:
        key = ForwardedFrom.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return ForwardedFrom(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
            signature=from_vertex.forward_signature,
            from_message_id=from_vertex.forward_from_message_id,
            date=from_vertex.forward_date,
        )


class ForwardedFromMethods:
    pass
