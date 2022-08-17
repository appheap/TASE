from pydantic import Field

from .base_document import BaseDocument
from ..enums import BotTaskType, BotTaskStatus


class BotTask(BaseDocument):
    _collection_name = "doc_bot_tasks"
    schema_version = 1

    user_id: int
    bot_id: int

    retry_count: int = Field(default=0)
    max_retry_count: int = Field(default=2)

    type: BotTaskType = Field(default=BotTaskType.UNKNOWN)
    status: BotTaskStatus = Field(default=BotTaskStatus.CREATED)
    state_dict: dict = Field(default=dict())  # todo: is it necessary?

    def update_status(
        self,
        status: BotTaskStatus,
    ) -> bool:
        """
        Update `status` of the task.

        Parameters
        ----------
        status : BotTaskStatus
            New status of the task

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if status is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.status = status
        return self.update(self_copy, reserve_non_updatable_fields=True)

    def update_retry_count(self) -> bool:
        """
        Update `retry_count` field of the task and set the task as `FAILED` if it exceeds the `max_retry_count` value.

        Returns
        -------
        bool
            Whether the update was successful or not

        Raises
        ------
        Exception
            If the `retry_count` was updated but could not update the `status` of the task

        """
        new_retry_count = self.retry_count + 1

        self_copy = self.copy(deep=True)
        self.retry_count = new_retry_count

        # todo: do this as a db transaction
        if self.update(self_copy, reserve_non_updatable_fields=True):
            if new_retry_count >= self.max_retry_count:
                return self.update_status(BotTaskStatus.FAILED)
        else:
            raise Exception("Could not update retry count field")


class BotTaskMethods:
    pass
