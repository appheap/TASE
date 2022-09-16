from typing import List, Optional

import apscheduler.triggers.base
from pydantic import BaseModel, Field

import tase


class BaseJob(BaseModel):
    """
    Abstract base class that defines the interface that every job must implement
    """

    name: str = Field(default=None)
    trigger: Optional[apscheduler.triggers.base.BaseTrigger] = Field(default=None)

    args: List[object] = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def run_job(
        self,
        db: "tase.db.DatabaseClient",
    ) -> None:
        pass
