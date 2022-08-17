from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import Chat, User


class IsCreatorOf(BaseEdge):
    """
    Connection from `Chat` to `User`.
    """

    _collection_name = "is_creator_of"
    schema_version = 1

    _from_vertex_collections = [Chat]
    _to_vertex_collections = [User]

    @classmethod
    def get_key(
        cls,
        from_vertex: Chat,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        return f"{from_vertex.key}:{to_vertex.key}"

    @classmethod
    def parse(
        cls,
        from_vertex: Chat,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional["IsCreatorOf"]:
        key = IsCreatorOf.parse_key(from_vertex, to_vertex)
        if key is None:
            return None

        return IsCreatorOf(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class IsCreatorOfMethods:
    pass
