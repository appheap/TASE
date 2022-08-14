from typing import Optional, Union

from arango import DocumentUpdateError, DocumentRevisionError

from .base_edge import BaseEdge
from ..vertices import Chat, Username
from ...enums import MentionSource


class Mentions(BaseEdge):
    """
    Connection from `Chat` to [`Chat`,`Username`]
    """

    _collection_edge_name = "mentions"

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [Chat, Username]

    is_direct_mention: bool
    mentioned_at: int
    mention_source: MentionSource
    mention_start_index: int
    from_message_id: int

    # this two attributes are only ment for connections from a `chat` to a `username`.
    checked_at: Optional[int]
    is_checked: Optional[bool]
    """
    whether this mention has been checked and, its effect has been calculated on the chat username extractor metadata
    """

    @staticmethod
    def parse(
        from_: Union[Chat, Username],
        to_: Union[Chat, Username],
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional["Mentions"]:
        key = Mentions.get_key(
            from_,
            to_,
            mentioned_at,
            mention_source,
            mention_start_index,
            from_message_id,
        )
        if not key:
            return None

        return (
            Mentions(
                key=key,
                from_node=from_,
                to_node=to_,
                is_direct_mention=is_direct_mention,
                mentioned_at=mentioned_at,
                mention_source=mention_source,
                mention_start_index=mention_start_index,
                from_message_id=from_message_id,
                is_checked=False if isinstance(to_, Username) else None,
            )
            if key
            else None
        )

    @staticmethod
    def get_key(
        from_: Union[Chat, Username],
        to_: Union[Chat, Username],
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional[str]:
        if (
            from_ is None
            or to_ is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None

        return f"{from_.key}:{to_.key}:{mentioned_at}:{from_message_id}:{mention_source.value}:{mention_start_index}"

    def check(
        self,
        is_checked: bool,
        checked_at: int,
    ) -> bool:

        try:
            self._db.update(
                {
                    "_key": self.key,
                    "is_checked": is_checked,
                    "checked_at": checked_at,
                },
                silent=True,
            )
            return True
        except DocumentUpdateError as e:
            pass
        except DocumentRevisionError as e:
            pass

        return False
