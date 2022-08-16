import pyrogram
from pydantic import Field
from pydantic.types import Enum
from pydantic.typing import Optional, List, Tuple

from .base_vertex import BaseVertex
from ...helpers import Restriction


class UserRole(Enum):
    UNKNOWN = 0
    SEARCHER = 1
    ADMIN = 2
    OWNER = 3


class User(BaseVertex):
    _collection_name = "users"
    _extra_do_not_update_fields = [
        "chosen_language_code",
        "role",
    ]

    user_id: int
    # is_contact : contact_of => User
    is_deleted: Optional[bool]
    is_bot: Optional[bool]
    is_verified: Optional[bool]
    is_restricted: Optional[bool]
    is_scam: Optional[bool]
    is_fake: Optional[bool]
    is_support: Optional[bool]
    is_premium: Optional[bool]
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    language_code: Optional[str]
    dc_id: Optional[int]
    phone_number: Optional[str]
    restrictions: Optional[List[Restriction]]

    # custom field that are not from telegram
    chosen_language_code: Optional[str]

    role: UserRole = Field(default=UserRole.SEARCHER)

    @classmethod
    def parse_key(
        cls,
        telegram_user: pyrogram.types.User,
    ) -> Optional[str]:
        if telegram_user is None:
            return None
        return str(telegram_user.id)

    @classmethod
    def parse(
        cls,
        telegram_user: pyrogram.types.User,
    ) -> Optional["User"]:
        if telegram_user is None:
            return None

        key = cls.parse_key(telegram_user)
        if key is None:
            return None

        return User(
            key=key,
            user_id=telegram_user.id,
            is_deleted=telegram_user.is_deleted,
            is_bot=telegram_user.is_bot,
            is_verified=telegram_user.is_verified,
            is_restricted=telegram_user.is_restricted,
            is_scam=telegram_user.is_scam,
            is_fake=telegram_user.is_fake,
            is_support=telegram_user.is_support,
            is_premium=telegram_user.is_premium,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
            language_code=telegram_user.language_code,
            dc_id=telegram_user.dc_id,
            phone_number=telegram_user.phone_number,
            restrictions=Restriction.parse_from_restrictions(telegram_user.restrictions),
        )

    def update_chosen_language(
        self,
        chosen_language_code: str,
    ) -> bool:
        if chosen_language_code is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.chosen_language_code = chosen_language_code
        return self.update(self_copy)


class UserMethods:
    def create_user(
        self,
        telegram_user: pyrogram.types.User,
    ) -> Tuple[Optional[User], bool]:
        """
        Create a user in the database from a telegram user object.

        Parameters
        ----------
        telegram_user : pyrogram.types.User
            Telegram user

        Returns
        -------
        Tuple[Optional[User], bool]
            User object and  `True` if the operation was successful, otherwise return `None` and `False`
        """
        if telegram_user is None:
            return None, False

        return User.insert(User.parse(telegram_user))

    def get_or_create_user(
        self,
        telegram_user: pyrogram.types.User,
    ) -> Optional[User]:
        """
        Get a user from the database if it exists, otherwise create a user in the database from a telegram user object.

        Parameters
        ----------
        telegram_user : pyrogram.types.User
            Telegram user

        Returns
        -------
        Optional[User]
            User object if the operation was successful, otherwise return `None`
        """
        if telegram_user is None:
            return None

        user = User.get(User.parse_key(telegram_user))
        if not user:
            # user does not exist in the database, create it
            user, successful = self.create_user(telegram_user)

        return user

    def update_or_create_user(
        self,
        telegram_user: pyrogram.types.User,
    ) -> Optional[User]:
        """
        Update a user in the database if it exists, otherwise create a user in the database from a telegram user
        object.

        Parameters
        ----------
        telegram_user : pyrogram.types.User
            Telegram user

        Returns
        -------
        Optional[User]
            User object if the operation was successful, otherwise return `None`
        """
        if telegram_user is None:
            return None

        user = User.get(User.parse_key(telegram_user))
        if user is not None:
            # user exists in the database, update it
            user, successful = user.update(User.parse(telegram_user))
        else:
            # user does not exist in the database, create it
            user, successful = self.create_user(telegram_user)

        if not user.is_bot:
            self.get_or_create_user_favorite_playlist(user)

        return user
