from typing import List, Optional

import pyrogram
from pydantic import Field
from pydantic.types import Enum

from .base_vertex import BaseVertex
from .restriction import Restriction


class Chat(BaseVertex):
    _vertex_name = "chats"
    _do_not_update = [
        "created_at",
        "last_indexed_offset_date",
        "last_indexed_offset_message_id",
        "importance_score",
    ]

    chat_id: int
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

    importance_score: Optional[float] = Field(default=0)
    last_indexed_offset_date: Optional[int] = Field(default=0)
    last_indexed_offset_message_id: Optional[int] = Field(default=1)

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

        return Chat(
            key=Chat.get_key(chat),
            chat_id=chat.id,
            chat_type=ChatType.parse_from_pyrogram(chat.type),
            is_verified=chat.is_verified,
            is_restricted=chat.is_restricted,
            is_scam=chat.is_scam,
            is_fake=chat.is_fake,
            is_support=chat.is_support,
            title=chat.title,
            username=chat.username,
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

    def update_importance_score(
        self,
        importance_score: float,
    ) -> bool:
        if importance_score is None:
            return False

        return self._db.update(
            {
                "_key": self.key,
                "importance_score": importance_score,
            },
            silent=True,
        )

    def update_offset_attributes(
        self,
        offset_id: int,
        offset_date: int,
    ) -> bool:
        """
        Updates offset attributes of the chat after being indexed

        Parameters
        ----------
        offset_id : int
            New offset id
        offset_date : int
            New offset date (it's a timestamp)

        Returns
        -------
        Whether the update was successful or not
        """
        if offset_id is None or offset_date is None:
            return False

        return self._db.update(
            {
                "_key": self.key,
                "last_indexed_offset_date": offset_date,
                "last_indexed_offset_message_id": offset_id,
            },
            silent=True,
        )


class ChatType(Enum):
    UNKNOWN = 0

    PRIVATE = 1
    "Chat is a private chat with a user"

    BOT = 2
    "Chat is a private chat with a bot"

    GROUP = 3
    "Chat is a basic group"

    SUPERGROUP = 4
    "Chat is a supergroup"

    CHANNEL = 5
    "Chat is a channel"

    @staticmethod
    def parse_from_pyrogram(
        chat_type: "pyrogram.enums.ChatType",
    ) -> Optional["ChatType"]:
        if chat_type is None:
            # fixme: how to avoid this?
            raise Exception("chat_type cannot be empty")

        return _from_pyrogram_mapping[chat_type.value]


_from_pyrogram_mapping = {
    pyrogram.enums.ChatType.PRIVATE.value: ChatType.PRIVATE,
    pyrogram.enums.ChatType.BOT.value: ChatType.BOT,
    pyrogram.enums.ChatType.GROUP.value: ChatType.GROUP,
    pyrogram.enums.ChatType.SUPERGROUP.value: ChatType.SUPERGROUP,
    pyrogram.enums.ChatType.CHANNEL.value: ChatType.CHANNEL,
}

# todo: how to fix this?
Chat.update_forward_refs()
