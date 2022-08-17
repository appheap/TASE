from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat, User


class IsMemberOf(BaseEdge):
    """
    Connection from `User` to `Chat`.
    """

    _collection_name = "is_member_of"
    schema_version = 1

    _from_vertex_collections = [User]
    _to_vertex_collections = [Chat]

    @classmethod
    def parse_key(
        cls,
        from_vertex: User,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: User,
        to_vertex: Chat,
        *args,
        **kwargs,
    ) -> Optional["IsMemberOf"]:

        key = IsMemberOf.parse_key(from_vertex, to_vertex)
        if not key:
            return None

        return IsMemberOf(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class IsMemberOfMethods:
    pass
