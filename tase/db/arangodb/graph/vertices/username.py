from typing import Optional

from pydantic import Field

from .base_vertex import BaseVertex


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

    def get_or_create_username(
        self,
        username: str,
    ) -> Optional[Username]:
        """
        Get Username if it exists in the ArangoDB, otherwise, create it.

        Parameters
        ----------
        username : str
            Username string to create the object from

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

        return db_username
