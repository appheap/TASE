from pydantic.typing import Optional

from .base_edge import BaseEdge
from ..vertices import User


class IsContactOf(BaseEdge):
    """
    Connection from a `User` to another `User`.
    """

    _collection_name = "is_contact_of"
    schema_version = 1

    _from_vertex_collections = [User]
    _to_vertex_collections = [User]

    @classmethod
    def parse(
        cls,
        from_vertex: User,
        to_vertex: User,
        *args,
        **kwargs,
    ) -> Optional["IsContactOf"]:
        key = IsContactOf.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return IsContactOf(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )


class IsContactOfMethods:
    pass
