from __future__ import annotations

from hashlib import sha1
from typing import Optional

from pydantic import Field

from aioarango.models import PersistentIndex
from .base_document import BaseDocument


class PlaylistInlineMessage(BaseDocument):
    __collection_name__ = "doc_playlist_inline_messages"
    schema_version = 1
    __non_updatable_fields__ = [
        "is_settings_visible",
    ]

    __indexes__ = [
        PersistentIndex(
            custom_version=1,
            name="bot_id",
            fields=[
                "bot_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="user_id",
            fields=[
                "user_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="inline_query_id",
            fields=[
                "inline_query_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="inline_message_id",
            fields=[
                "inline_message_id",
            ],
        ),
    ]

    bot_id: int
    user_id: int
    inline_query_id: str
    inline_message_id: Optional[str]

    is_settings_visible: Optional[bool] = Field(default=False)

    @classmethod
    def parse_key(
        cls,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
    ) -> Optional[str]:
        if bot_id is None or user_id is None or inline_query_id is None:
            return None

        return sha1(f"{bot_id}#{user_id}#{inline_query_id}".encode("utf-8")).hexdigest()

    @classmethod
    def parse(
        cls,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        inline_message_id: str = None,
    ) -> Optional[PlaylistInlineMessage]:
        key = cls.parse_key(
            bot_id,
            user_id,
            inline_query_id,
        )
        if key is None:
            return None

        return PlaylistInlineMessage(
            key=key,
            bot_id=bot_id,
            user_id=user_id,
            inline_query_id=inline_query_id,
            inline_message_id=inline_message_id,
        )

    async def toggle_settings_visibility(self) -> bool:

        self_copy: PlaylistInlineMessage = self.copy(deep=True)
        self_copy.is_settings_visible = not self.is_settings_visible

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
        )

    async def set_inline_message_id(
        self,
        inline_message_id: str,
    ) -> bool:
        if inline_message_id is None or not len(inline_message_id):
            return False

        self_copy: PlaylistInlineMessage = self.copy(deep=True)
        self_copy.inline_message_id = inline_message_id

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
        )


class PlaylistInlineMessageMethods:
    async def create_playlist_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        inline_message_id: str = None,
    ) -> Optional[PlaylistInlineMessage]:
        doc, successful = await PlaylistInlineMessage.insert(
            PlaylistInlineMessage.parse(
                bot_id,
                user_id,
                inline_query_id,
                inline_message_id,
            )
        )
        if doc and successful:
            return doc

        return None

    async def get_or_create_playlist_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        inline_message_id: str = None,
    ) -> Optional[PlaylistInlineMessage]:
        playlist_inline_message = await PlaylistInlineMessage.get(
            PlaylistInlineMessage.parse_key(
                bot_id,
                user_id,
                inline_query_id,
            )
        )
        if playlist_inline_message is None:
            playlist_inline_message = await self.create_playlist_inline_message(
                bot_id,
                user_id,
                inline_query_id,
                inline_message_id,
            )

        return playlist_inline_message

    async def find_playlist_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
    ) -> Optional[PlaylistInlineMessage]:
        if bot_id is None or user_id is None or inline_query_id is None:
            return None

        return await PlaylistInlineMessage.get(
            PlaylistInlineMessage.parse_key(
                bot_id,
                user_id,
                inline_query_id,
            )
        )

    async def set_playlist_inline_message_id(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        inline_message_id: str,
    ) -> bool:
        if bot_id is None or user_id is None or inline_query_id is None:
            return False
        playlist_inline_message = await self.get_or_create_playlist_inline_message(
            bot_id,
            user_id,
            inline_query_id,
            inline_message_id,
        )
        if playlist_inline_message:
            return await playlist_inline_message.set_inline_message_id(inline_message_id)

        return False

    async def find_playlist_inline_message_by_message_inline_id(
        self,
        bot_id: int,
        user_id: int,
        inline_message_id: str,
    ) -> Optional[PlaylistInlineMessage]:
        if bot_id is None or user_id is None or inline_message_id is None or not len(inline_message_id):
            return None

        return await PlaylistInlineMessage.find_one(
            filters={
                "bot_id": bot_id,
                "user_id": user_id,
                "inline_message_id": inline_message_id,
            }
        )
