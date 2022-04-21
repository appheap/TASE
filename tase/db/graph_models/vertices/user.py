from dataclasses import dataclass
from typing import Optional, List

import arrow
import pyrogram

from .base_vertex import BaseVertex
from .restriction import Restriction


@dataclass
class User(BaseVertex):
    _vertex_name = 'users'

    user_id: int
    # is_contact : contact_of => User
    is_deleted: bool
    is_bot: bool
    is_verified: bool
    is_restricted: bool
    is_scam: bool
    is_fake: bool
    is_support: bool
    first_name: Optional['str']
    last_name: Optional['str']
    username: Optional['str']
    language_code: Optional['str']
    dc_id: Optional['int']
    phone_number: Optional['str']
    restrictions: List[Restriction]

    def parse_for_graph(self) -> dict:
        super_dict = super(User, self).parse_for_graph()

        super_dict.update(
            {
                '_id': self.id,
                '_key': self.key,
                '_rev': self.rev,
                'user_id': self.user_id,
                'is_deleted': self.is_deleted,
                'is_bot': self.is_bot,
                'is_verified': self.is_verified,
                'is_restricted': self.is_restricted,
                'is_scam': self.is_scam,
                'is_fake': self.is_fake,
                'is_support': self.is_support,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'username': self.username,
                'language_code': self.language_code,
                'dc_id': self.dc_id,
                'phone_number': self.phone_number,
                'restrictions': Restriction.parse_all_for_graph(self.restrictions)
            }
        )

        return super_dict

    @staticmethod
    def parse_from_user(user: 'pyrogram.types.User') -> Optional['User']:
        if user is None:
            return None

        ts = int(arrow.utcnow().timestamp())

        return User(
            id=None,
            key=str(user.id),
            rev=None,
            created_at=ts,
            modified_at=ts,
            user_id=user.id,
            is_deleted=user.is_deleted,
            is_bot=user.is_bot,
            is_verified=user.is_verified,
            is_restricted=user.is_restricted,
            is_scam=user.is_scam,
            is_fake=user.is_fake,
            is_support=user.is_support,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            dc_id=user.dc_id,
            phone_number=user.phone_number,
            restrictions=Restriction.parse_from_restrictions(user.restrictions)
        )
