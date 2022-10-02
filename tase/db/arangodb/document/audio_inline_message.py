from __future__ import annotations

from hashlib import sha1
from typing import Optional

from .base_document import BaseDocument


class AudioInlineMessage(BaseDocument):
    _collection_name = "doc_audio_inline_messages"
    schema_version = 1

    bot_id: int
    user_id: int
    inline_query_id: str
    inline_message_id: Optional[str]

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
    ) -> Optional[AudioInlineMessage]:
        key = cls.parse_key(bot_id, user_id, inline_query_id)
        if key is None:
            return None

        return AudioInlineMessage(
            key=key,
            bot_id=bot_id,
            user_id=user_id,
            inline_query_id=inline_query_id,
        )

    def set_inline_message_id(
        self,
        inline_message_id: str,
    ) -> bool:
        if inline_message_id is None or not len(inline_message_id):
            return False

        self_copy: AudioInlineMessage = self.copy(deep=True)
        self_copy.inline_message_id = inline_message_id

        return self.update(
            self_copy,
            reserve_non_updatable_fields=False,
        )


class AudioInlineMessageMethods:
    def create_audio_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
    ) -> Optional[AudioInlineMessage]:
        doc, successful = AudioInlineMessage.insert(
            AudioInlineMessage.parse(
                bot_id,
                user_id,
                inline_query_id,
            )
        )
        if doc and successful:
            return doc

        return None

    def get_or_create_audio_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
    ) -> Optional[AudioInlineMessage]:
        audio_inline_message = AudioInlineMessage.get(
            AudioInlineMessage.parse_key(
                bot_id,
                user_id,
                inline_query_id,
            )
        )
        if audio_inline_message is None:
            audio_inline_message = self.create_audio_inline_message(
                bot_id,
                user_id,
                inline_query_id,
            )

        return audio_inline_message

    def find_audio_inline_message(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
    ) -> Optional[AudioInlineMessage]:
        if bot_id is None or user_id is None or inline_query_id is None:
            return None

        key = AudioInlineMessage.parse_key(
            bot_id,
            user_id,
            inline_query_id,
        )
        return AudioInlineMessage.get(key)

    def set_audio_inline_message_id(
        self,
        bot_id: int,
        user_id: int,
        inline_query_id: str,
        inline_message_id: str,
    ) -> bool:
        if bot_id is None or user_id is None or inline_query_id is None:
            return False
        audio_inline_message = self.find_audio_inline_message(
            bot_id,
            user_id,
            inline_query_id,
        )
        if audio_inline_message:
            return audio_inline_message.set_inline_message_id(inline_message_id)

        return False

    def find_audio_inline_message_by_message_inline_id(
        self,
        bot_id: int,
        user_id: int,
        inline_message_id: str,
    ) -> Optional[AudioInlineMessage]:
        if (
            bot_id is None
            or user_id is None
            or inline_message_id is None
            or not len(inline_message_id)
        ):
            return None

        return AudioInlineMessage.find_one(
            filters={
                "bot_id": bot_id,
                "user_id": user_id,
                "inline_message_id": inline_message_id,
            }
        )
