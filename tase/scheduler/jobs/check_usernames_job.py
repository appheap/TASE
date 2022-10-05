import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin

import tase
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...telegram.client import TelegramClient
from ...telegram.tasks import CheckUsernamesTask


class CheckUsernamesJob(BaseJob):
    type = RabbitMQTaskType.CHECK_USERNAMES_JOB

    trigger = IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        self.task_in_worker(db)
        usernames = db.graph.get_unchecked_usernames()

        for username in usernames:
            # todo: blocking or non-blocking? which one is better suited for this case?

            CheckUsernamesTask(
                kwargs={
                    "username": username,
                }
            ).publish(db)

        self.task_done(db)
