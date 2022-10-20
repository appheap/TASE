from __future__ import annotations

from typing import Optional, Generator, Tuple

from pydantic import Field

from tase.common.utils import get_now_timestamp
from tase.errors import InvalidFromVertex, InvalidToVertex
from tase.my_logger import logger
from . import Chat
from .base_vertex import BaseVertex
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
    ) -> Optional[Username]:
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
    _get_unchecked_usernames_query = (
        "for username in @usernames"
        "   filter username.is_checked == false and username.modified_at < @now"
        "   sort username.created_at desc"
        "   return username"
    )

    _get_checked_usernames_with_unchecked_mentions = (
        "for username in @usernames"
        "   filter username.is_checked == true and username.modified_at < @now"
        "   sort username.created_at desc"
        "   let unchecked_mentions_count = ("
        "       for chat, mention_e in 1..1 inbound username graph '@graph_name' options {order: 'dfs', edgeCollections: ['@mentions'], vertexCollections: ['@chats']}"
        "           filter mention_e.modified_at < @now and mention_e.is_checked == false"
        "           collect with count into len"
        "           return len"
        "           )"
        "   sort unchecked_mentions_count desc"
        "   let mentioned_chat = ("
        "       for chat, e in 1..1 inbound username graph '@graph_name' options {order: 'dfs', edgeCollections: ['@has'], vertexCollections: ['@chats']}"
        "           return chat"
        "       )"
        "   return {username_:username, mentioned_chat_:mentioned_chat[0], count_:unchecked_mentions_count[0]}"
    )

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

    def get_username_by_key(
        self,
        key: str,
    ) -> Optional[Username]:
        """
        Get `Username` by its 'key` f it exists in the ArangoDB.

        Parameters
        ----------
        key : str
            Key to get the `Username` vertex by

        Returns
        -------
        Username, optional
            Username if it exists in the ArangoDB, otherwise, return None.

        """
        if key is None:
            return None

        return Username.get(key)

    def create_username(
        self,
        username: str,
    ) -> Optional[Username]:
        """
        Create a Username in the ArangoDB.

        Parameters
        ----------
        username : str
            Username string to create the object from

        Returns
        -------
        Username, optional
            Username object if creation was successful, otherwise, return None.

        """
        if username is None or not len(username):
            return None

        db_username, successful = Username.insert(Username.parse(username))
        if db_username and successful:
            return db_username
        else:
            return None

    def get_or_create_username(
        self,
        username: str,
        chat: Chat = None,
        is_direct_mention: bool = None,
        mentioned_at: int = None,
        mention_source: MentionSource = None,
        mention_start_index: int = None,
        from_message_id: int = None,
        create_mention_edge: bool = True,
    ) -> Optional[Username]:
        """
        Get Username if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        username : str
            Username string to create the object from
        chat : Chat
            Chat where this username is mentioned
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
        create_mention_edge : bool, default : True
            Whether to create the mentions edge or not

        Returns
        -------
        Username, optional
            Username object if operation was successful, otherwise, return None.

        """

        if username is None or not len(username):
            return None

        db_username = Username.get(Username.parse_key(username))
        if db_username is None:
            db_username = self.create_username(username)

        if db_username and create_mention_edge:
            if (
                chat is None
                or is_direct_mention is None
                or mentioned_at is None
                or mention_source is None
                or mention_start_index is None
                or from_message_id is None
            ):
                return None

            from tase.db.arangodb.graph.edges import Mentions

            if chat.username is not None:
                if chat.username.lower() != username.lower():
                    # this is not a self-mention edge, so it should be created
                    create_mention_edge_ = True
                else:
                    # don't create self-mention edges
                    create_mention_edge_ = False
            else:
                # the username is mentioned from a chat that doesn't have a username itself
                create_mention_edge_ = True

            if create_mention_edge_:
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
                except (InvalidFromVertex, InvalidToVertex):
                    logger.error("ValueError: could not create the `Mentions`edge from `Chat` vertex to `Username` vertex")

        return db_username

    def get_unchecked_usernames(self) -> Generator[Username, None, None]:
        """
        Get list of Usernames that have not been checked yet, sorted by their creation date in a ascending order

        Yields
        -------
        Username
            List of Username objects that have not been checked yet
        """

        # only get those username that have been modified more than 15 minutes ago
        now = get_now_timestamp() - 15 * 60 * 1000

        cursor = Username.execute_query(
            self._get_unchecked_usernames_query,
            bind_vars={
                "usernames": Username._collection_name,
                "now": now,
            },
        )

        if cursor is not None and len(cursor):
            for doc in cursor:
                yield Username.from_collection(doc)

    def get_checked_usernames_with_unchecked_mentions(
        self,
    ) -> Generator[Tuple[Username, Chat], None, None]:
        """
        Get list of Usernames that have been checked, but they have mentions that have not been checked,
        sorted by the number of unchecked `mentions` edges in a descending order

        Yields
        -------
        Username
            List of Username objects
        """

        # only get those username that have been modified more than 15 minutes ago
        now = get_now_timestamp() - 15 * 60 * 1000

        from tase.db.arangodb.graph.edges import Mentions
        from tase.db.arangodb.graph.edges import Has

        cursor = Username.execute_query(
            self._get_checked_usernames_with_unchecked_mentions,
            bind_vars={
                "usernames": Username._collection_name,
                "mentions": Mentions._collection_name,
                "chats": Chat._collection_name,
                "has": Has._collection_name,
                "now": now,
            },
        )

        if cursor is not None and len(cursor):
            for doc in cursor:
                count = int(doc.get("count_", None))
                if count > 0:
                    username = Username.from_collection(doc.get("username_", None))
                    mentioned_chat = Chat.from_collection(doc.get("mentioned_chat_", None))
                    yield username, mentioned_chat
