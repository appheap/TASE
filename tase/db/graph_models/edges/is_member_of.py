from typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat, User


class IsMemberOf(BaseEdge):
    """
    Connection from `User` to `Chat`.
    """

    _collection_edge_name = "is_member_of"

    _from_vertex_collections = [User]
    _to_vertex_collections = [Chat]

    @staticmethod
    def parse_from_user_and_chat(
        user: User,
        chat: Chat,
    ) -> Optional["IsMemberOf"]:

        key = IsMemberOf.get_key(user, chat)
        if not key:
            return None

        return IsMemberOf(
            key=key,
            from_node=user,
            to_node=chat,
        )

    @classmethod
    def get_key(
        cls,
        user: User,
        chat: Chat,
    ) -> str:
        if chat is None or user is None:
            return ""

        return f"{user.key}@{chat.key}"
