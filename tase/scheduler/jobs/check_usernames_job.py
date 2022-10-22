import random
import time

import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin

import tase
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...telegram.client import TelegramClient
from ...telegram.tasks import CheckUsernameTask


class CheckUsernamesJob(BaseJob):
    type = RabbitMQTaskType.CHECK_USERNAMES_JOB
    priority = 1

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

        for idx, username in enumerate(usernames):
            # todo: blocking or non-blocking? which one is better suited for this case?

            if idx > 0 and idx % 10 == 0:
                # fixme: sleep to avoid publishing many tasks while the others haven't been processed yet
                time.sleep(10 * random.randint(10, 15))

            CheckUsernameTask(
                kwargs={
                    "username_key": username.key,
                }
            ).publish(db)

        self.task_done(db)
