from typing import Optional

from arango import DocumentUpdateError, DocumentRevisionError
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

    def check(
        self,
        is_checked: bool,
        checked_at: int,
        is_valid: bool,
    ) -> bool:
        if is_checked is None or checked_at is None or is_valid is None:
            return False

        try:
            self._db.update(
                {
                    "_key": self.key,
                    "is_checked": is_checked,
                    "checked_at": checked_at,
                    "is_valid": is_valid,
                },
                silent=True,
            )
            return True
        except DocumentUpdateError as e:
            pass
        except DocumentRevisionError as e:
            pass

        return False
