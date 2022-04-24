from typing import List, Optional

import pyrogram

from .base_vertex import BaseVertex
from .restriction import Restriction


class Chat(BaseVertex):
    _vertex_name = 'chats'

    chat_id: int
    chat_type: str
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

    @staticmethod
    def get_key(chat: 'pyrogram.types.Chat'):
        return f'{chat.id}'

    @staticmethod
    def parse_from_chat(chat: 'pyrogram.types.Chat') -> Optional['Chat']:
        if chat is None:
            return None

        return Chat(
            key=Chat.get_key(chat),
            chat_id=chat.id,
            chat_type=chat.type,
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
