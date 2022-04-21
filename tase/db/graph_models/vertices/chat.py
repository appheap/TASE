from dataclasses import dataclass
from typing import List, Optional

import arrow
import pyrogram

from .base_vertex import BaseVertex
from .restriction import Restriction


@dataclass
class Chat(BaseVertex):
    _vertex_name = 'chats'

    chat_id: int
    chat_type: str
    is_verified: bool
    is_restricted: bool
    # is_creator: creator => User
    is_scam: bool
    is_fake: bool
    is_support: bool
    title: Optional['str']
    username: Optional['str']
    first_name: Optional['str']
    last_name: Optional['str']
    bio: Optional['str']
    description: Optional['str']
    dc_id: Optional['int']
    has_protected_content: bool
    invite_link: Optional['str']
    restrictions: List[Restriction]
    # linked_chat: linked_chat => Chat
    available_reactions: List['str']
    member_count: Optional['int']
    distance: Optional['int']

    def parse_for_graph(self) -> dict:
        super_dict = super(Chat, self).parse_for_graph()
        super_dict.update(
            {
                'chat_id': self.chat_id,
                'chat_type': self.chat_type,
                'is_verified': self.is_verified,
                'is_restricted': self.is_restricted,
                'is_scam': self.is_scam,
                'is_fake': self.is_fake,
                'is_support': self.is_support,
                'title': self.title,
                'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'bio': self.bio,
                'description': self.description,
                'dc_id': self.dc_id,
                'has_protected_content': self.has_protected_content,
                'invite_link': self.invite_link,
                'restrictions': Restriction.parse_all_for_graph(self.restrictions),
                'available_reactions': self.available_reactions,
                'member_count': self.member_count,
                'distance': self.distance,
            }
        )
        return super_dict

    @staticmethod
    def parse_from_chat(chat: 'pyrogram.types.Chat') -> Optional['Chat']:
        if chat is None:
            return None

        ts = int(arrow.utcnow().timestamp())
        return Chat(
            id=None,
            key=str(chat.id),
            rev=None,
            created_at=ts,
            modified_at=ts,
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
