from typing import Optional

from pydantic import Field

from .base_document import BaseDocument


class ChatUsernameBuffer(BaseDocument):
    """
    This class is for buffering chat usernames that are being extracted from messages before adding them to the
    database for indexing
    """

    _doc_collection_name = "doc_chat_username_buffers"

    username: Optional[str]
    is_checked: bool = Field(default=False)

    @staticmethod
    def parse_from_username(
        username: str,
    ) -> Optional["ChatUsernameBuffer"]:
        if username is None:
            return None

        return ChatUsernameBuffer(
            key=ChatUsernameBuffer.get_key(username),
            username=username.lower(),
        )

    @staticmethod
    def get_key(username: str) -> str:
        return username.lower().encode("ascii", "ignore").strip().decode()
