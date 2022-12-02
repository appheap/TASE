from __future__ import annotations

import uuid
from typing import Optional

from pydantic import Field

from aioarango.models import PersistentIndex
from tase.errors import UpdateRetryCountFailed
from .base_document import BaseDocument
from ..enums import BotTaskType, BotTaskStatus


class BotTask(BaseDocument):
    _collection_name = "doc_bot_tasks"
    schema_version = 1
    _extra_indexes = [
        PersistentIndex(
            custom_version=1,
            name="user_id",
            fields=[
                "user_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="bot_id",
            fields=[
                "bot_id",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="type",
            fields=[
                "type",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="status",
            fields=[
                "status",
            ],
        ),
    ]

    user_id: int
    bot_id: int

    retry_count: int = Field(default=0)
    max_retry_count: int = Field(default=2)

    type: BotTaskType = Field(default=BotTaskType.UNKNOWN)
    status: BotTaskStatus = Field(default=BotTaskStatus.CREATED)
    state_dict: dict = Field(default=dict())  # todo: is it necessary?

    async def update_status(
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
        return await self.update(self_copy, reserve_non_updatable_fields=True)

    async def update_retry_count(self) -> bool:
        """
        Update `retry_count` field of the task and set the task as `FAILED` if it exceeds the `max_retry_count` value.

        Returns
        -------
        bool
            Whether the update was successful or not

        Raises
        ------
        UpdateRetryCountFailed
            If the `retry_count` was updated but could not update the `status` of the task

        """
        new_retry_count = self.retry_count + 1

        self_copy = self.copy(deep=True)
        self.retry_count = new_retry_count

        # todo: do this as a db transaction
        if await self.update(self_copy, reserve_non_updatable_fields=False):
            if new_retry_count >= self.max_retry_count:
                return await self.update_status(BotTaskStatus.FAILED)
            return True
        else:
            raise UpdateRetryCountFailed()

    @classmethod
    def parse(
        cls,
        user_id: int,
        bot_id: int,
        task_type: BotTaskType,
        state_dict: dict = None,
    ) -> Optional[BotTask]:
        if user_id is None or bot_id is None or task_type is None:
            return None

        bot_task = BotTask(
            key=str(uuid.uuid4()),
            user_id=user_id,
            bot_id=bot_id,
            type=task_type,
        )
        if state_dict is not None and len(state_dict):
            bot_task.state_dict = state_dict

        return bot_task

    async def update_task_state_dict(
        self,
        new_task_state: dict,
    ) -> bool:
        """
        Update the task extra parameters dictionary.

        Parameters
        ----------
        new_task_state : dict
            Dictionary of the new extra parameters

        Returns
        -------
        bool
            Whether the update was successful or not
        """
        if new_task_state is None:
            return False

        self_copy = self.copy(deep=True)
        self_copy.state_dict = new_task_state
        return await self.update(self_copy, reserve_non_updatable_fields=True)


class BotTaskMethods:
    _cancel_recent_bot_tasks_query = (
        "for doc_task in @doc_bot_tasks"
        "   sort doc_task.modified_at desc"
        "   filter doc_task.type == @type and doc_task.status == @status and doc_task.user_id == @user_id and doc_task.bot_id == @bot_id"
        "   update doc_task with {"
        "       status: @new_status"
        "   } in @doc_bot_tasks options {mergeObjects: true}"
        "   return NEW"
    )

    _get_latest_bot_task_query = (
        "for doc_task in @doc_bot_tasks"
        "   filter doc_task.status == @status and doc_task.user_id == @user_id and doc_task.bot_id == @bot_id"
        "   sort doc_task.modified_at desc"
        "   limit 1"
        "   return doc_task"
    )

    async def create_bot_task(
        self,
        user_id: int,
        bot_id: int,
        task_type: BotTaskType,
        state_dict: dict = None,
        cancel_recent_task: bool = True,
    ) -> Optional[BotTask]:
        """
        Create a `BotTask` document in the ArangoDB.

        Parameters
        ----------
        user_id : int
            ID of the Telegram User
        bot_id : int
            ID of the BOT this task belongs to
        task_type : BotTaskType
            Type of the task
        state_dict : dict
            Extra data passed to the BotTask
        cancel_recent_task : bool, default : True
            Whether to cancel recent tasks of the user before creating a new one

        Returns
        -------
        BotTask, optional
            BotTask document if the creation was successful, otherwise, return None
        """
        if cancel_recent_task:
            await self.cancel_recent_bot_task(
                user_id,
                bot_id,
                task_type,
            )

        task, successful = await BotTask.insert(
            BotTask.parse(
                user_id,
                bot_id,
                task_type,
                state_dict,
            )
        )
        if task and successful:
            return task

        return None

    async def cancel_recent_bot_task(
        self,
        user_id: int,
        bot_id: int,
        task_type: BotTaskType,
    ) -> bool:
        """
        Cancel the most recent bot task for the specified user.

        Parameters
        ----------
        user_id : int
            ID of the Telegram User to cancel the task for
        bot_id : int
            ID of the Telegram Bot which the task made for
        task_type : BotTaskType
            Type of the BotTask to cancel

        Returns
        -------
        bool
            Whether the cancellation was successful or not.
        """
        if user_id is None or bot_id is None or task_type is None:
            return False

        cursor = await BotTask.execute_query(
            self._cancel_recent_bot_tasks_query,
            bind_vars={
                "doc_bot_tasks": BotTask._collection_name,
                "type": task_type.value,
                "user_id": user_id,
                "bot_id": bot_id,
                "status": BotTaskStatus.CREATED.value,
                "new_status": BotTaskStatus.CANCELED.value,
            },
        )
        return cursor is not None

    async def get_latest_bot_task(
        self,
        user_id: int,
        bot_id: int,
    ) -> Optional[BotTask]:
        """
        Get the latest created bot task for the specified user id.

        Parameters
        ----------
        user_id : int
            ID of the Telegram User that this task belongs to
        bot_id : int
            ID of the Telegram Bot that the task made for

        Returns
        -------
        BotTask, optional
            Latest BotTask for the given user ID if it exists, otherwise, return None
        """
        if user_id is None or bot_id is None:
            return

        async with await BotTask.execute_query(
            self._get_latest_bot_task_query,
            bind_vars={
                "doc_bot_tasks": BotTask._collection_name,
                "user_id": user_id,
                "bot_id": bot_id,
                "status": BotTaskStatus.CREATED.value,
            },
        ) as cursor:
            async for doc in cursor:
                return BotTask.from_collection(doc)

        return None
