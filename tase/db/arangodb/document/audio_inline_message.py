from __future__ import annotations

from hashlib import sha1
from typing import Optional

from aioarango.models import PersistentIndex
from .base_document import BaseDocument


class AudioInlineMessage(BaseDocument):
    _collection_name = "doc_audio_inline_messages"
    schema_version = 1
    _extra_indexes = [
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
        PersistentIndex(
            custom_version=1,
            name="hit_download_url",
            fields=[
                "hit_download_url",
            ],
        ),
    ]

    bot_id: int
    user_id: int
    inline_query_id: str
    inline_message_id: Optional[str]

    hit_download_url: str

    @classmethod
    def parse_key(
        cls,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        hit_download_url: str,
    ) -> Optional[str]:
        if bot_id is None or user_id is None or inline_query_id is None:
            return None

        return sha1(f"{bot_id}#{user_id}#{inline_query_id}#{hit_download_url}".encode("utf-8")).hexdigest()

    @classmethod
    def parse(
        cls,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        hit_download_url: str,
        inline_message_id: str = None,
    ) -> Optional[AudioInlineMessage]:
        key = cls.parse_key(
            bot_id,
            user_id,
            inline_query_id,
            hit_download_url,
        )
        if key is None:
            return None

        return AudioInlineMessage(
            key=key,
            bot_id=bot_id,
            user_id=user_id,
            inline_query_id=inline_query_id,
            hit_download_url=hit_download_url,
            inline_message_id=inline_message_id,
        )

    async def set_inline_message_id(
        self,
        inline_message_id: str,
    ) -> bool:
        if inline_message_id is None or not len(inline_message_id):
            return False

        self_copy: AudioInlineMessage = self.copy(deep=True)
        self_copy.inline_message_id = inline_message_id

        return await self.update(
            self_copy,
            reserve_non_updatable_fields=False,
        )


class AudioInlineMessageMethods:
    async def create_audio_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        hit_download_url: str,
        inline_message_id: str = None,
    ) -> Optional[AudioInlineMessage]:
        doc, successful = await AudioInlineMessage.insert(
            AudioInlineMessage.parse(
                bot_id,
                user_id,
                inline_query_id,
                hit_download_url,
                inline_message_id,
            )
        )
        if doc and successful:
            return doc

        return None

    async def get_or_create_audio_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        hit_download_url: str,
        inline_message_id: str = None,
    ) -> Optional[AudioInlineMessage]:
        audio_inline_message = await AudioInlineMessage.get(
            AudioInlineMessage.parse_key(
                bot_id,
                user_id,
                inline_query_id,
                hit_download_url,
            )
        )
        if audio_inline_message is None:
            audio_inline_message = await self.create_audio_inline_message(
                bot_id,
                user_id,
                inline_query_id,
                hit_download_url,
                inline_message_id,
            )

        return audio_inline_message

    async def find_audio_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        hit_download_url: str,
    ) -> Optional[AudioInlineMessage]:
        if bot_id is None or user_id is None or inline_query_id is None:
            return None

        return await AudioInlineMessage.get(
            AudioInlineMessage.parse_key(
                bot_id,
                user_id,
                inline_query_id,
                hit_download_url,
            )
        )

    async def set_audio_inline_message_id(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        hit_download_url: str,
        inline_message_id: str,
    ) -> bool:
        if bot_id is None or user_id is None or inline_query_id is None:
            return False
        audio_inline_message = await self.get_or_create_audio_inline_message(
            bot_id,
            user_id,
            inline_query_id,
            hit_download_url,
            inline_message_id,
        )
        if audio_inline_message:
            return await audio_inline_message.set_inline_message_id(inline_message_id)

        return False

    async def find_audio_inline_message_by_message_inline_id(
        self,
        bot_id: int,
        user_id: int,
        inline_message_id: str,
        hit_download_url: str,
    ) -> Optional[AudioInlineMessage]:
        if bot_id is None or user_id is None or inline_message_id is None or not len(inline_message_id):
            return None

        return await AudioInlineMessage.find_one(
            filters={
                "bot_id": bot_id,
                "user_id": user_id,
                "inline_message_id": inline_message_id,
                "hit_download_url": hit_download_url,
            }
        )
