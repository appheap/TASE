from typing import List, Optional

from pydantic import BaseModel, Field

from tase.db.database_client import DatabaseClient
from tase.telegram.client import TelegramClient


class BaseTask(BaseModel):
    name: Optional[str] = Field(default=None)
    args: List[object] = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)

    def run_task(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
    ):
        raise NotImplementedError
