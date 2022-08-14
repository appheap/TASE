from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat, User


class IsCreatorOf(BaseEdge):
    """
    Connection from `Chat` to `User`.
    """

    _collection_edge_name = "is_creator_of"

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [User]

    @staticmethod
    def parse_from_chat_and_user(
        chat: Chat,
        creator: User,
    ) -> Optional["IsCreatorOf"]:
        key = IsCreatorOf.get_key(chat, creator)
        if not key:
            return None

        return IsCreatorOf(
            key=key,
            from_node=chat,
            to_node=creator,
        )

    @classmethod
    def get_key(
        cls,
        chat: Chat,
        creator: User,
    ) -> str:
        if chat is None or creator is None:
            return ""

        return f"{chat.key}@{creator.key}"
