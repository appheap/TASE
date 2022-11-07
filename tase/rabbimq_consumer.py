from typing import Optional

from aio_pika.abc import AbstractRobustConnection
from pydantic import BaseModel

from tase.db import DatabaseClient


class RabbitMQConsumer(BaseModel):
    db: DatabaseClient
    connection: Optional[AbstractRobustConnection]

    class Config:
        arbitrary_types_allowed = True
