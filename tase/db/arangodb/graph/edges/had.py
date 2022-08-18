from pydantic.typing import Optional, Union

from . import Has
from .base_edge import BaseEdge
from ..vertices import (
    Audio,
    Playlist,
    User,
)


class Had(BaseEdge):
    _collection_name = "had"
    schema_version = 1

    deleted_at: int
    metadata_created_at: int
    metadata_modified_at: int

    _from_vertex_collections = (
        User,
        Playlist,
    )
    _to_vertex_collections = (
        Playlist,
        Audio,
    )

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[User, Playlist],
        to_vertex: Union[Playlist, Audio],
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        deleted_at = kwargs.get("deleted_at", None)
        if deleted_at is None:
            raise KeyError("`deleted_at` or/and `has` keyword arguments haven't been provided")

        if not isinstance(deleted_at, int):
            raise ValueError(
                f"Wrong value passed for argument `deleted_at`, expected `int` got `{type(deleted_at)}` instead"
            )

        return f"{from_vertex.key}:{to_vertex.key}:{deleted_at}"

    @classmethod
    def parse(
        cls,
        from_vertex: Union[User, Playlist],
        to_vertex: Union[User, Playlist],
        *args,
        **kwargs,
    ) -> Optional["Had"]:
        """
        Create a `Had` edge object with the arguments provided and return it if successful, otherwise return `None`.

        Parameters
        ----------
        from_vertex : Union[User, Playlist]
            Start of the edge
        to_vertex : Union[User, Playlist]
            End of the edge
        args : Any
            Arguments provided to this function
        kwargs : Dict[str, Any]
            Keyword arguments provided to this function.

        Returns
        -------
        Optional[Had]
            Had edge object if given arguments are valid, otherwise return `None`

        Raises
        ------
        KeyError
            When the required keyword arguments haven't been passed to the function
        ValueError.
            When the start or the end vertex provided to the function does not match the edge definition in the
            database.
        TypeError
            When the given keyword arguments have invalid types.


        """
        super(Had, cls).parse(from_vertex, to_vertex, *args, **kwargs)

        # check if the required keyword arguments are present
        deleted_at = kwargs.get("deleted_at", None)
        has = kwargs.get("has", None)
        if deleted_at is None or has is None:
            raise KeyError("`deleted_at` or/and `has` keyword arguments haven't been provided")

        if not isinstance(deleted_at, int):
            raise TypeError(
                f"Wrong value passed for argument `deleted_at`, expected `int` got `{type(deleted_at)}` instead"
            )

        if not isinstance(has, Has):
            raise TypeError(
                f"Wrong value passed for argument `has`, expected `{Has.__class__.__name__}` got `{type(deleted_at)}`"
            )

        key = Had.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        if has is None:
            return None

        return Had(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
            deleted_at=deleted_at,
            metadata_created_at=has.created_at,
            metadata_modified_at=has.modified_at,
        )


class HadMethods:
    pass