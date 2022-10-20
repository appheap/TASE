from __future__ import annotations

import collections
from enum import Enum
from typing import Optional, List, TYPE_CHECKING, Dict, Any, Union

import pyrogram
from pydantic import Field
from pyrogram.types import BotCommandScopeChat, BotCommandScopeDefault

from tase.common.utils import prettify, get_now_timestamp
from tase.my_logger import logger
from .base_vertex import BaseVertex

if TYPE_CHECKING:
    from .. import ArangoGraphMethods
from ...helpers import Restriction


class UserRole(Enum):
    UNKNOWN = 0
    SEARCHER = 1
    ADMIN = 2
    OWNER = 3


class User(BaseVertex):
    _collection_name = "users"
    schema_version = 1

    _extra_do_not_update_fields = [
        "chosen_language_code",
        "role",
        "has_interacted_with_bot",
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

    created_from_telegram_chat: bool
    has_interacted_with_bot: bool = Field(default=False)

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
        telegram_user: Union[pyrogram.types.User, pyrogram.types.Chat],
    ) -> Optional[User]:
        if telegram_user is None:
            return None

        key = cls.parse_key(telegram_user)
        if key is None:
            return None

        if isinstance(telegram_user, pyrogram.types.Chat):
            is_bot = telegram_user.type == pyrogram.enums.ChatType.BOT
            is_premium = None
            language_code = None
            phone_number = None
            created_from_telegram_chat = True
        elif isinstance(telegram_user, pyrogram.types.User):
            is_bot = telegram_user.is_bot
            is_premium = telegram_user.is_premium
            language_code = telegram_user.language_code
            phone_number = telegram_user.phone_number
            created_from_telegram_chat = False
        else:
            is_bot = None
            is_premium = None
            language_code = None
            phone_number = None
            created_from_telegram_chat = False

        return User(
            key=key,
            user_id=telegram_user.id,
            is_deleted=getattr(telegram_user, "is_deleted", None),
            is_bot=is_bot,
            is_verified=telegram_user.is_verified,
            is_restricted=telegram_user.is_restricted,
            is_scam=telegram_user.is_scam,
            is_fake=telegram_user.is_fake,
            is_support=telegram_user.is_support,
            is_premium=is_premium,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username.lower() if telegram_user.username else None,
            language_code=language_code,
            dc_id=telegram_user.dc_id,
            phone_number=phone_number,
            restrictions=Restriction.parse_from_restrictions(telegram_user.restrictions),
            created_from_telegram_chat=created_from_telegram_chat,
        )

    def update_chosen_language(
        self,
        chosen_language_code: str,
    ) -> bool:
        if chosen_language_code is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.chosen_language_code = chosen_language_code
        return self.update(self_copy, reserve_non_updatable_fields=False)

    def update_role(
        self,
        role: UserRole,
    ) -> bool:
        if role is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.role = role
        return self.update(self_copy, reserve_non_updatable_fields=False)

    def update_has_interacted_with_bot(
        self,
        new_value: bool,
    ) -> bool:
        if new_value is None:
            return False

        self_copy: User = self.copy(deep=True)
        self_copy.has_interacted_with_bot = new_value
        return self.update(self_copy, reserve_non_updatable_fields=False)


class UserMethods:
    _get_admin_and_owners_query = "for user in @users" "   filter user.role in @roles_list" "   sort user.role desc" "   return user"

    _get_new_joined_users_count_query = (
        "for user in @users"
        "   filter user.has_interacted_with_bot == true and user.created_at >= @checkpoint"
        "   collect with count into new_joined_users_count"
        "   return new_joined_users_count"
    )

    _get_total_interacted_users_count = (
        "for user in @users"
        "   filter user.has_interacted_with_bot == true"
        "   collect with count into total_users_count"
        "   return total_users_count"
    )

    def _get_or_create_favorite_playlist(
        self: ArangoGraphMethods,
        user: User,
    ):
        if not user.is_bot:
            fav_playlist = self.get_or_create_favorite_playlist(user)
            if not fav_playlist:
                # fixme: could not create/get favorite playlist.
                logger.error(f"could not create/get favorite playlist for user: {prettify(user)}")

    def create_user(
        self: ArangoGraphMethods,
        telegram_user: Union[pyrogram.types.User, pyrogram.types.Chat],
    ) -> Optional[User]:
        """
        Create a user in the database from a telegram user object.

        Parameters
        ----------
        telegram_user : pyrogram.types.User
            Telegram user

        Returns
        -------
        User, optional
            User object and  `True` if the operation was successful, otherwise return `None` and `False`
        """
        if telegram_user is None:
            return None

        user, successful = User.insert(User.parse(telegram_user))
        if user and successful:
            self._get_or_create_favorite_playlist(user)
            return user

        return None

    def get_or_create_user(
        self: ArangoGraphMethods,
        telegram_user: Union[pyrogram.types.User, pyrogram.types.Chat],
    ) -> Optional[User]:
        """
        Get a user from the database if it exists, otherwise create a user in the database from a telegram user object.

        Parameters
        ----------
        telegram_user : pyrogram.types.User
            Telegram user

        Returns
        -------
        User, optional
            User object if the operation was successful, otherwise return `None`
        """
        if telegram_user is None:
            return None

        user = User.get(User.parse_key(telegram_user))
        if not user:
            # user does not exist in the database, create it
            user = self.create_user(telegram_user)

        else:
            # check if the user vertex was created from a telegram chat object, if that is the case, then update the
            # user with the new object before returning
            if user.created_from_telegram_chat and isinstance(telegram_user, pyrogram.types.User):
                self.update_or_create_user(telegram_user)

        return user

    def get_interacted_user(
        self,
        telegram_user: pyrogram.types.User,
        update: bool = False,
    ) -> Optional[User]:
        """
        Get the `User` vertex if it exists in the ArangoDb, otherwise, create it. set the `has_interacted_with_bot`
        property of the user if it is set to `False`

        Parameters
        ----------
        telegram_user : pyrogram.types.User
            Telegram user to get/create/update the vertex from
        update : bool, default : False
            Whether to update the vertex from the telegram object or not. Default is set to False.

        Returns
        -------
        User, optional
            User object if the operation was successful, otherwise, return None

        """
        if telegram_user is None:
            return None

        user = self.update_or_create_user(telegram_user) if update else self.get_or_create_user(telegram_user)
        if user and not user.has_interacted_with_bot:
            user.update_has_interacted_with_bot(True)

        return user

    def update_or_create_user(
        self: ArangoGraphMethods,
        telegram_user: Union[pyrogram.types.User, pyrogram.types.Chat],
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
        User, optional
            User object if the operation was successful, otherwise return `None`
        """
        if telegram_user is None:
            return None

        user: User = User.get(User.parse_key(telegram_user))
        if user is not None:
            # user exists in the database, update it
            updated = user.update(User.parse(telegram_user))
        else:
            # user does not exist in the database, create it
            user = self.create_user(telegram_user)

        return user

    def get_user_by_telegram_id(
        self,
        user_id: int,
    ) -> Optional[User]:
        """
        Get User by Telegram user ID

        Parameters
        ----------
        user_id : int
            Telegram user ID

        Returns
        -------
        User, optional
            User if it exists in the ArangoDB, otherwise, return None.

        """
        if user_id is None:
            return None

        return User.get(str(user_id))

    def get_admins_and_owners(self) -> List[User]:
        cursor = User.execute_query(
            self._get_admin_and_owners_query,
            bind_vars={
                "users": User._collection_name,
                "roles_list": [UserRole.OWNER.value, UserRole.ADMIN.value],
            },
        )
        res = collections.deque()
        if cursor is not None and len(cursor):
            for doc in cursor:
                res.append(User.from_collection(doc))

        return list(res)

    @classmethod
    def get_bot_command_for_telegram_user(
        cls,
        user: User,
        role: UserRole,
    ) -> dict:
        from tase.telegram.bots.bot_commands import BaseCommand

        return {
            "scope": BotCommandScopeChat(user.user_id),
            "commands": BaseCommand.populate_commands(user.role if role is None else role),
        }

    @classmethod
    def get_bot_commands_list_for_telegram(
        cls,
        admins_and_owners: List[User],
    ) -> List[Dict[str, Any]]:
        """
        Get list of bot commands along with scope of the commands used in Telegram

        Parameters
        ----------
        admins_and_owners : list of graph_models.vertices.User
            List of `User` vertices that are their role is either `admin` or `owner`

        Returns
        -------
        list[dict[str, any]]
            List of dictionary containing the scope of a bot command and list of bot commands

        """

        from tase.telegram.bots.bot_commands import BaseCommand

        res = collections.deque()
        for user_vertex in admins_and_owners:
            if user_vertex is not None and user_vertex.role in (
                UserRole.ADMIN,
                UserRole.OWNER,
            ):
                res.append(
                    {
                        "scope": BotCommandScopeChat(user_vertex.user_id),
                        "commands": BaseCommand.populate_commands(user_vertex.role),
                    }
                )

        res.append(
            {
                "scope": BotCommandScopeDefault(),
                "commands": BaseCommand.populate_commands(UserRole.SEARCHER),
            }
        )

        return list(res)

    def get_user_by_username(
        self,
        username: str,
    ) -> Optional[User]:
        """
        Get `User` vertex by its `username`

        Parameters
        ----------
        username : str
            Username to find the user by

        Returns
        -------
        User, optional
            User if it exists by the given username, otherwise, return None

        """
        if username is None:
            return None

        return User.find_one({"username": username.lower()})

    def get_new_joined_users_count(self) -> int:
        """
        Get the total number of joined users in the last 24 hours

        Returns
        -------
        int
            Total number joined users in the last 24 hours

        """
        checkpoint = get_now_timestamp() - 86400000

        cursor = User.execute_query(
            self._get_new_joined_users_count_query,
            bind_vars={
                "users": User._collection_name,
                "checkpoint": checkpoint,
            },
        )

        if cursor is not None and len(cursor):
            return int(cursor.pop())

        return 0

    def get_total_users_count(self) -> int:
        """
        Get the total number of users who have interacted with the bot

        Returns
        -------
        int
            Total number of users who have interacted with the bot

        """
        cursor = User.execute_query(
            self._get_total_interacted_users_count,
            bind_vars={
                "users": User._collection_name,
            },
        )

        if cursor is not None and len(cursor):
            return int(cursor.pop())

        return 0
