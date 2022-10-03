import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin

import tase
from .base_job import BaseJob
from ...telegram.tasks import CheckUsernamesTask


class CheckUsernamesJob(BaseJob):
    name = "check_usernames_job"
    trigger = IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ) -> None:
        usernames = db.graph.get_unchecked_usernames()

        for username in usernames:
            # todo: blocking or non-blocking? which one is better suited for this case?

            CheckUsernamesTask(
                kwargs={
                    "username": username,
                }
            ).publish()
