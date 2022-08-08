from typing import Optional

from pydantic import Field

from .base_vertex import BaseVertex


class Username(BaseVertex):
    """
    This class is for buffering chat usernames that are being extracted from messages before adding them to the
    database for indexing
    """

    _vertex_name = "usernames"

    username: Optional[str]
    is_checked: bool = Field(default=False)
    checked_at: Optional[int]
    is_valid: Optional[bool]

    @staticmethod
    def parse_from_username(
        username: str,
    ) -> Optional["Username"]:
        if username is None:
            return None

        return Username(
            key=Username.get_key(username),
            username=username.lower(),
        )

    @staticmethod
    def get_key(username: str) -> str:
        return username.lower()
