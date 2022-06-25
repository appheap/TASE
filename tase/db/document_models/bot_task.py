from pydantic import Field
from pydantic.types import Enum

from .base_document import BaseDocument


class BotTaskType(Enum):
    UNKNOWN = 0
    CREATE_NEW_PLAYLIST = 1
    EDIT_PLAYLIST_TITLE = 2
    EDIT_PLAYLIST_DESCRIPTION = 3
    DELETE_PLAYLIST = 4


class BotTaskStatus(Enum):
    UNKNOWN = 0
    CREATED = 1
    DONE = 2
    CANCELED = 3
    DELETED = 4
    FAILED = 5


class BotTask(BaseDocument):
    _doc_collection_name = "doc_bot_tasks"

    user_id: int
    bot_id: int

    retry_count: int = Field(default=0)
    max_retry_count: int = Field(default=5)

    type: BotTaskType = Field(default=BotTaskType.UNKNOWN)
    status: BotTaskStatus = Field(default=BotTaskStatus.CREATED)
    state_dict: dict = Field(default=dict())  # todo: is it necessary?

    def update_status(
        self,
        status: "BotTaskStatus",
    ):
        if status is None:
            return

        self._db.update(
            {
                "_key": self.key,
                "status": status.value,
            },
            silent=True,
        )

    def update_retry_count(self):
        self._db.update(
            {
                "_key": self.key,
                "retry_count": self.retry_count + 1,
            },
            silent=True,
        )

        if self.retry_count + 1 >= self.max_retry_count:
            self.update_status(BotTaskStatus.FAILED)
