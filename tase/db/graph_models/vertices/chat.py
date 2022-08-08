from typing import List, Optional

import pyrogram
from pydantic import Field

from .base_vertex import BaseVertex
from .indexer_metadata import IndexerMetadata
from .restriction import Restriction
from ...enums import ChatType


class Chat(BaseVertex):
    _vertex_name = "chats"
    _do_not_update = [
        "created_at",
        "audio_indexer_metadata",
        "username_extractor_metadata",
    ]

    chat_id: int
    is_public: bool
    chat_type: "ChatType"
    is_verified: Optional[bool]
    is_restricted: Optional[bool]
    # is_creator: creator => User
    is_scam: Optional[bool]
    is_fake: Optional[bool]
    is_support: Optional[bool]
    title: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    description: Optional[str]
    dc_id: Optional[int]
    has_protected_content: Optional[bool]
    invite_link: Optional[str]
    restrictions: Optional[List[Restriction]]
    # linked_chat: linked_chat => Chat
    available_reactions: Optional[List[str]]
    member_count: Optional[int]
    distance: Optional[int]

    audio_indexer_metadata: IndexerMetadata = Field(default=IndexerMetadata())
    username_extractor_metadata: IndexerMetadata = Field(default=IndexerMetadata())

    @staticmethod
    def get_key(
        chat: "pyrogram.types.Chat",
    ):
        return f"{chat.id}"

    @staticmethod
    def parse_from_chat(
        chat: "pyrogram.types.Chat",
    ) -> Optional["Chat"]:
        if chat is None:
            return None

        chat_type = ChatType.parse_from_pyrogram(chat.type)

        return Chat(
            key=Chat.get_key(chat),
            chat_id=chat.id,
            is_public=Chat.get_is_public(chat, chat_type),
            chat_type=chat_type,
            is_verified=chat.is_verified,
            is_restricted=chat.is_restricted,
            is_scam=chat.is_scam,
            is_fake=chat.is_fake,
            is_support=chat.is_support,
            title=chat.title,
            username=chat.username.lower() if chat.username else None,  # it's useful for searching by username
            first_name=chat.first_name,
            last_name=chat.last_name,
            bio=chat.bio,
            description=chat.description,
            dc_id=chat.dc_id,
            has_protected_content=chat.has_protected_content,
            invite_link=chat.invite_link,
            restrictions=Restriction.parse_from_restrictions(chat.restrictions),
            available_reactions=chat.available_reactions,
            member_count=chat.members_count,
            distance=chat.distance,
        )

    @staticmethod
    def get_is_public(
        chat: pyrogram.types.Chat,
        chat_type: ChatType,
    ) -> bool:
        """
        Check whether a chat is public or not

        Parameters
        ----------
        chat : pyrogram.types.Chat
            Chat object from pyrogram
        chat_type : ChatType
            Type of the chat

        Returns
        -------
        Whether the chat is public or not
        """
        is_public = False
        if chat_type in (ChatType.PRIVATE, ChatType.BOT):
            is_public = True
        elif chat_type == ChatType.GROUP:
            is_public = False
        elif chat_type in (ChatType.CHANNEL, ChatType.SUPERGROUP):
            if chat.username:
                is_public = True
            else:
                is_public = False

        return is_public


# todo: how to fix this?
Chat.update_forward_refs()
