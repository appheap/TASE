from typing import Optional

from pydantic import Field

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
    from_message_id: int

    is_checked: bool = Field(default=False)
    """
    whether this mention has been checked and, its effect has been calculated on the chat username extractor metadata
    """

    @staticmethod
    def parse_from_chat_and_username(
        chat: "Chat",
        username: "Username",
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional["Mentions"]:
        if (
            chat is None
            or username is None
            or is_direct_mention is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None

        key = Mentions.get_key(
            chat,
            username,
            mentioned_at,
            mention_source,
            mention_start_index,
            from_message_id,
        )
        return (
            Mentions(
                key=key,
                from_node=chat,
                to_node=username,
                is_direct_mention=is_direct_mention,
                mentioned_at=mentioned_at,
                mention_source=mention_source,
                from_message_id=from_message_id,
            )
            if key
            else None
        )

    @staticmethod
    def get_key(
        chat: "Chat",
        username: "Username",
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional[str]:
        if (
            chat is None
            or username is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None

        return (
            f"{chat.key}:{username.key}:{mentioned_at}:{from_message_id}:{mention_source.value}:{mention_start_index}"
        )
