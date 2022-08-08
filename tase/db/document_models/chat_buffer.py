from typing import Optional

import pyrogram
from pydantic import Field

from .base_document import BaseDocument
from .. import graph_db
from ..enums import ChatType


class ChatBuffer(BaseDocument):
    """
    This class is for buffering chats that are being extracted from messages before adding them to the database for
    indexing
    """

    _doc_collection_name = "doc_chat_buffers"

    chat_id: int
    is_public: bool
    chat_type: "ChatType"

    username: Optional[str]
    invite_link: Optional[str]

    title: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    description: Optional[str]

    members_count: Optional[int]
    dc_id: Optional[int]

    is_checked: bool = Field(default=False)

    @staticmethod
    def parse_from_chat(
        chat: "pyrogram.types.Chat",
    ) -> Optional["ChatBuffer"]:
        if chat is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(chat.type)

        return ChatBuffer(
            key=ChatBuffer.get_key(chat),
            chat_id=chat.id,
            is_public=graph_db.vertices.Chat.get_is_public(chat, chat_type),
            chat_type=chat_type,
            username=chat.username,
            invite_link=chat.invite_link,
            title=chat.title,
            first_name=chat.first_name,
            last_name=chat.last_name,
            description=chat.description if chat.description else chat.bio,
            members_count=chat.members_count,
            dc_id=chat.dc_id,
        )

    @staticmethod
    def get_key(chat: pyrogram.types.Chat) -> str:
        return str(chat.id)
