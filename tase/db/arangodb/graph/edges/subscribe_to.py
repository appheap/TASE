from __future__ import annotations

from typing import Optional, Tuple

from pydantic import Field

from tase.my_logger import logger
from .base_edge import BaseEdge, EdgeEndsValidator
from ..vertices import (
    User,
    Playlist,
)


class SubscribeTo(BaseEdge):
    __collection_name__ = "subscribe_to"
    schema_version = 1

    __from_vertex_collections__ = (User,)
    __to_vertex_collections__ = (Playlist,)

    __non_updatable_fields__ = ("is_active",)

    is_active: bool = Field(default=True)

    @classmethod
    @EdgeEndsValidator
    def parse(
        cls,
        from_vertex: User,
        to_vertex: Playlist,
        *args,
        **kwargs,
    ) -> Optional[SubscribeTo]:
        key = SubscribeTo.parse_key(from_vertex, to_vertex, *args, **kwargs)
        if key is None:
            return None

        return SubscribeTo(
            key=key,
            from_node=from_vertex,
            to_node=to_vertex,
        )

    async def toggle(self) -> bool:
        self_copy: SubscribeTo = self.copy(deep=True)
        self_copy.is_active = not self.is_active

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
        )


class SubscribeToMethods:
    async def toggle_playlist_subscription(
        self,
        user_vertex: User,
        playlist_vertex: Playlist,
    ) -> Tuple[bool, bool]:
        subscribed = False
        successful = False

        if not user_vertex or not playlist_vertex:
            return successful, subscribed

        subscribe_to_edge: Optional[SubscribeTo] = await SubscribeTo.get(SubscribeTo.parse_key(user_vertex, playlist_vertex))
        if not subscribe_to_edge:
            if not await SubscribeTo.create_edge(user_vertex, playlist_vertex):
                logger.error(f"Error in creating `{SubscribeTo.__class__.__name__}` edge from `{user_vertex.key}` to `{playlist_vertex.key}`")
                subscribed = False
                successful = False
            else:
                subscribed = True
                successful = True
        else:
            successful = await subscribe_to_edge.toggle()
            subscribed = subscribe_to_edge.is_active

        return successful, subscribed
