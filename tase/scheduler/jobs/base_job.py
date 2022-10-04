from typing import Optional

import apscheduler.triggers.base
from pydantic import Field

from tase.task_distribution import BaseTask, TargetWorkerType


class BaseJob(BaseTask):
    """
    Abstract base class that defines the interface that every job must implement
    """

    trigger: Optional[apscheduler.triggers.base.BaseTrigger] = Field(default=None)
    target_worker_type = TargetWorkerType.SCHEDULER_JOB

    class Config:
        arbitrary_types_allowed = True
