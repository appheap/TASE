from __future__ import annotations

import collections
from enum import Enum
from typing import Optional, List, TYPE_CHECKING, Dict, Any

import pyrogram
from pydantic import Field
from pyrogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from tase.common.utils import prettify
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
    ) -> Optional[User]:
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
            restrictions=Restriction.parse_from_restrictions(
                telegram_user.restrictions
            ),
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


class UserMethods:
    _get_admin_and_owners_query = (
        "for user in @users"
        "   filter user.role in @roles_list"
        "   sort user.role desc"
        "   return user"
    )

    def create_user(
        self,
        telegram_user: pyrogram.types.User,
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
            return user

        return None

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
        User, optional
            User object if the operation was successful, otherwise return `None`
        """
        if telegram_user is None:
            return None

        user = User.get(User.parse_key(telegram_user))
        if not user:
            # user does not exist in the database, create it
            user = self.create_user(telegram_user)

        return user

    def update_or_create_user(
        self: ArangoGraphMethods,
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

        if not user.is_bot:
            fav_playlist = self.get_or_create_favorite_playlist(user)
            if not fav_playlist:
                # fixme: could not create/get favorite playlist.
                logger.error(
                    f"could not create/get favorite playlist for user: {prettify(user)}"
                )

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

        from tase.telegram.bots.bot_commands import BaseCommand, BotCommandType

        def populate_commands(role: UserRole) -> List[BaseCommand]:
            commands = collections.deque()
            for command in sorted(
                filter(
                    lambda c: c is not None,
                    map(
                        BaseCommand.get_command,
                        filter(
                            lambda c_type: c_type
                            not in (
                                BotCommandType.INVALID,
                                BotCommandType.UNKNOWN,
                                BotCommandType.BASE,
                            ),
                            list(BotCommandType),
                        ),
                    ),
                ),
                key=lambda c: str(c.command_type.value),
            ):
                bot_command = BotCommand(
                    str(command.command_type.value),
                    command.command_description,
                )
                if command.required_role_level.value <= role.value:
                    commands.append(bot_command)

            return list(commands)

        res = collections.deque()
        for user_vertex in admins_and_owners:
            if user_vertex.role in (UserRole.ADMIN, UserRole.OWNER):
                res.append(
                    {
                        "scope": BotCommandScopeChat(user_vertex.user_id),
                        "commands": populate_commands(user_vertex.role),
                    }
                )

        res.append(
            {
                "scope": BotCommandScopeDefault(),
                "commands": populate_commands(UserRole.SEARCHER),
            }
        )

        return list(res)
