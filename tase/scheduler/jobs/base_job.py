from typing import Optional

import apscheduler.triggers.base
from pydantic import Field

from tase.db import DatabaseClient
from tase.task_distribution import BaseTask


class BaseJob(BaseTask):
    """
    Abstract base class that defines the interface that every job must implement
    """

    trigger: Optional[apscheduler.triggers.base.BaseTrigger] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def run_job(
        self,
        db: DatabaseClient,
    ) -> None:
        raise NotImplementedError
