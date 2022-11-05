from __future__ import annotations

from typing import Optional, Union

from tase.errors import ParamNotProvided
from .base_edge import BaseEdge, EdgeEndsValidator
from .has import Has
from ..vertices import (
    Audio,
    Playlist,
    User,
    Keyword,
)
from ...base.index import PersistentIndex


class Had(BaseEdge):
    _collection_name = "had"
    schema_version = 1
    _extra_indexes = [
        PersistentIndex(
            version=1,
            name="deleted_at",
            fields=[
                "deleted_at",
            ],
        ),
        PersistentIndex(
            version=1,
            name="metadata_created_at",
            fields=[
                "metadata_created_at",
            ],
        ),
        PersistentIndex(
            version=1,
            name="metadata_modified_at",
            fields=[
                "metadata_modified_at",
            ],
        ),
    ]

    deleted_at: int
    metadata_created_at: int
    metadata_modified_at: int

    _from_vertex_collections = (
        User,
        Playlist,
        Audio,
    )
    _to_vertex_collections = (
        Playlist,
        Audio,
        Keyword,
    )

    @classmethod
    def parse_key(
        cls,
        from_vertex: Union[User, Playlist, Audio],
        to_vertex: Union[Playlist, Audio, Keyword],
        *args,
        **kwargs,
    ) -> Optional[str]:
        if from_vertex is None or to_vertex is None:
            return None

        deleted_at = kwargs.get("deleted_at", None)
        if deleted_at is None:
            raise ParamNotProvided("deleted_at")

        if not isinstance(deleted_at, int):
            raise ValueError(f"Wrong value passed for argument `deleted_at`, expected `int` got `{type(deleted_at)}` instead")

        return f"{from_vertex.key}:{to_vertex.key}:{deleted_at}"

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: Union[User, Playlist],
        to_vertex: Union[User, Playlist],
        *args,
        **kwargs,
    ) -> Optional[Had]:
        """
        Create a `Had` edge object with the arguments provided and return it if successful, otherwise return `None`.

        Parameters
        ----------
        from_vertex : Union[User, Playlist]
            Start of the edge
        to_vertex : Union[User, Playlist]
            End of the edge
        args : tuple
            Arguments provided to this function
        kwargs : dict, optional
            Keyword arguments provided to this function.

        Returns
        -------
        Had, optional
            Had edge object if given arguments are valid, otherwise return `None`

        Raises
        ------
        ParamNotProvided
            When the required keyword arguments haven't been passed to the function
        ValueError.
            When the start or the end vertex provided to the function does not match the edge definition in the
            database.
        TypeError
            When the given keyword arguments have invalid types.


        """

        # check if the required keyword arguments are present
        deleted_at = kwargs.get("deleted_at", None)
        has = kwargs.get("has", None)
        if deleted_at is None:
            raise ParamNotProvided("deleted_at")
        if has is None:
            raise ParamNotProvided("has")

        if not isinstance(deleted_at, int):
            raise TypeError(f"Wrong value passed for argument `deleted_at`, expected `int` got `{type(deleted_at)}` instead")

        if not isinstance(has, Has):
            raise TypeError(f"Wrong value passed for argument `has`, expected `{Has.__class__.__name__}` got `{type(deleted_at)}`")

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
