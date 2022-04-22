from typing import Optional, List

import pyrogram

from .base_vertex import BaseVertex
from .restriction import Restriction


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
    restrictions: Optional[List[Restriction]]

    @staticmethod
    def parse_from_user(user: 'pyrogram.types.User') -> Optional['User']:
        if user is None:
            return None

        return User(
            key=str(user.id),
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
