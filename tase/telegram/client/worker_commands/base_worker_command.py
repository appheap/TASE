from typing import Optional

from kombu.mixins import ConsumerProducerMixin
from pydantic import BaseModel, Field

import tase


class BaseWorkerCommand(BaseModel):
    name: Optional[str] = Field(default=None)

    def run_command(
        self,
        consumer_producer: ConsumerProducerMixin,
        telegram_client: "tase.telegram.client.TelegramClient",
        db: "tase.db.DatabaseClient",
    ) -> None:
        raise NotImplementedError
