from typing import Optional

from pydantic import Field

from tase.my_logger import logger
from . import Chat
from .base_vertex import BaseVertex
from ..edges import Mentions
from ...enums import MentionSource


class Username(BaseVertex):
    """
    This class is for buffering chat usernames that are being extracted from messages before adding them to the
    database for indexing
    """

    _collection_name = "usernames"
    schema_version = 1

    username: Optional[str]
    is_checked: bool = Field(default=False)
    checked_at: Optional[int]
    is_valid: Optional[bool]

    @classmethod
    def parse(
        cls,
        username: str,
    ) -> Optional["Username"]:
        if username is None:
            return None

        return Username(
            key=Username.parse_key(username),
            username=username.lower(),
        )

    @classmethod
    def parse_key(
        cls,
        username: str,
    ) -> str:
        return username.lower()

    def check(
        self,
        is_checked: bool,
        checked_at: int,
        is_valid: bool,
    ) -> bool:
        """
        Check the Username object with the given parameters.

        Parameters
        ----------
        is_checked : bool
            Whether this username is checked or not
        checked_at : bool
            Timestamp when this username `is_checked` was updated
        is_valid : bool
            Whether this username is valid or not.

        Returns
        -------
        bool
            Whether the update was successful or not.
        """
        if is_checked is None or checked_at is None or is_valid is None:
            return False

        self_copy: Username = self.copy(deep=True)
        self_copy.is_checked = is_checked
        self_copy.checked_at = checked_at
        self_copy.is_valid = is_valid

        return self.update(self_copy)


class UsernameMethods:
    def get_username(
        self,
        username: str,
    ) -> Optional[Username]:
        """
        Get `Username` if it exists in the ArangoDB.

        Parameters
        ----------
        username : str
            Username string to get the `Username` vertex by

        Returns
        -------
        Username, optional
            Username if it exists in the ArangoDB, otherwise, return None.

        """
        if username is None:
            return None

        return Username.get(Username.parse_key(username))

    def create_username(
        self,
        chat: Chat,
        username: str,
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional[Username]:
        """
        Create a Username in the ArangoDB.

        Parameters
        ----------
        chat : Chat
            Chat where this username is mentioned
        username : str
            Username string to create the object from
        is_direct_mention: bool
            Whether this username was mentioned in text/caption of a message or not
        mentioned_at : int
            Timestamp when this mention happened
        mention_source : int
            Source of the mentioned username. Mention can directly can be extracted within text or file attributes.
        mention_start_index : int
            Starting index of mentioned username in the source
        from_message_id : int
            Telegram Message ID of the message where the username was mentioned

        Returns
        -------
        Username, optional
            Username object if creation was successful, otherwise, return None.

        """
        if (
            chat is None
            or username is None
            or not len(username)
            or is_direct_mention is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None

        db_username, successful = Username.insert(Username.parse(username))
        if db_username and successful:

            if chat.username is not None:
                if chat.username.lower() != username.lower():
                    # this is not a self-mention edge, so it should be created
                    create_mention_edge = True
                else:
                    # don't create self-mention edges
                    create_mention_edge = False
            else:
                # the username is mentioned from a chat that doesn't have a username itself
                create_mention_edge = True

            if create_mention_edge:
                # mentioned username is not self-mention, create the edge from `Chat` vertex to `Username` vertex
                try:
                    Mentions.get_or_create_edge(
                        chat,
                        db_username,
                        is_direct_mention,
                        mentioned_at,
                        mention_source,
                        mention_start_index,
                        from_message_id,
                    )
                except ValueError:
                    logger.error(
                        "ValueError: could not create the `Mentions`edge from `Chat` vertex to `Username` vertex"
                    )

            return db_username
        else:
            return None

    def get_or_create_username(
        self,
        chat: Chat,
        username: str,
        is_direct_mention: bool,
        mentioned_at: int,
        mention_source: MentionSource,
        mention_start_index: int,
        from_message_id: int,
    ) -> Optional[Username]:
        """
        Get Username if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        chat : Chat
            Chat where this username is mentioned
        username : str
            Username string to create the object from
        is_direct_mention: bool
            Whether this username was mentioned in text/caption of a message or not
        mentioned_at : int
            Timestamp when this mention happened
        mention_source : int
            Source of the mentioned username. Mention can directly can be extracted within text or file attributes.
        mention_start_index : int
            Starting index of mentioned username in the source
        from_message_id : int
            Telegram Message ID of the message where the username was mentioned

        Returns
        -------
        Username, optional
            Username object if operation was successful, otherwise, return None.

        """
        if (
            chat is None
            or username is None
            or not len(username)
            or is_direct_mention is None
            or mentioned_at is None
            or mention_source is None
            or mention_start_index is None
            or from_message_id is None
        ):
            return None

        db_username = Username.get(Username.parse_key(username))
        if db_username is None:
            db_username = self.create_username(
                chat,
                username,
                is_direct_mention,
                mentioned_at,
                mention_source,
                mention_start_index,
                from_message_id,
            )

        return db_username
