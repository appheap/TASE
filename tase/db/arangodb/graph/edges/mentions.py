from pydantic.typing import Optional, Union

from .base_edge import BaseEdge
from ..vertices import Chat, Username
from ...enums import MentionSource


class Mentions(BaseEdge):
    """
    Connection from `Chat` to [`Chat`,`Username`]
    """

    _collection_name = "mentions"
    schema_version = 1

    _from_vertex_collections = (Chat,)
    _to_vertex_collections = (
        Chat,
        Username,
    )

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

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[Chat, Username],
        to_vertex: Union[Chat, Username],
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if (
            from_vertex is None
            or to_vertex is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None

        return f"{from_vertex.key}:{to_vertex.key}:{mentioned_at}:{from_message_id}:{mention_source.value}:{mention_start_index}"

    @classmethod
    def parse(
        cls,
        from_vertex: Union[Chat, Username],
        to_vertex: Union[Chat, Username],
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
        *args,
        **kwargs,
    ) -> Optional["Mentions"]:
        key = Mentions.parse_key(
            from_vertex,
            to_vertex,
            mentioned_at,
            mention_source,
            mention_start_index,
            from_message_id,
        )
        if key is None:
            return None

        return Mentions(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
            is_direct_mention=is_direct_mention,
            mentioned_at=mentioned_at,
            mention_source=mention_source,
            mention_start_index=mention_start_index,
            from_message_id=from_message_id,
            is_checked=False if isinstance(to_vertex, Username) else None,
        )

    def check(
        self,
        is_checked: bool,
        checked_at: int,
    ) -> bool:
        self_copy = self.copy(deep=True)
        self_copy.is_checked = is_checked
        self_copy.checked_at = checked_at

        return self.update(self_copy, reserve_non_updatable_fields=False)


class MentionsMethods:
    pass
