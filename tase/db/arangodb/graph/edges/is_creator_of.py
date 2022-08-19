from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat, User


class IsCreatorOf(BaseEdge):
    """
    Connection from `Chat` to `User`.
    """

    _collection_name = "is_creator_of"
    schema_version = 1

    _from_vertex_collections = (User,)
    _to_vertex_collections = (Chat,)

    @classmethod
    def parse(
        cls,
        from_vertex: User,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional["IsCreatorOf"]:
        key = IsCreatorOf.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return IsCreatorOf(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class IsCreatorOfMethods:
    pass
