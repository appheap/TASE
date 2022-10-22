import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin

from tase.db import DatabaseClient
from tase.my_logger import logger
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType


class DummyJob(BaseJob):
    type = RabbitMQTaskType.DUMMY_JOB
    priority = 1

    trigger = IntervalTrigger(
        seconds=5,
        start_date=arrow.now().datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        self.task_in_worker(db)
        logger.info(f"{self.type.value} : {self.kwargs}")
        self.task_done(db)
