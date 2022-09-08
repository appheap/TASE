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
        if is_checked is None or checked_at is None or is_valid is None:
            return False

        self_copy: Username = self.copy(deep=True)
        self_copy.is_checked = is_checked
        self_copy.checked_at = checked_at
        self_copy.is_valid = is_valid

        return self.update(self_copy)


class UsernameMethods:
    pass
