from typing import Optional

from .base_edge import BaseEdge
from ..vertices import InlineQuery, Query, User


class HasMade(BaseEdge):
    """
    Connection from `User` to `InlineQuery` or `Query
    """

    _collection_edge_name = "has_made"

    _from_vertex_collections = [User]
    _to_vertex_collections = [InlineQuery, Query]

    @staticmethod
    def parse_from_user_and_inline_query(
        user: "User", inline_query: "InlineQuery"
    ) -> Optional["HasMade"]:
        if inline_query is None or user is None:
            return None

        key = f"{user.key}@{inline_query.key}"
        return HasMade(
            key=key,
            from_node=user,
            to_node=inline_query,
        )

    @staticmethod
    def parse_from_user_and_query(user: "User", query: "Query") -> Optional["HasMade"]:
        if query is None or user is None:
            return None

        key = f"{user.key}@{query.key}"
        return HasMade(
            key=key,
            from_node=user,
            to_node=query,
        )
