import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.my_logger import logger
from .base_job import BaseJob
from ...telegram.client import TelegramClient
from tase.telegram.tasks import ExtractUsernamesTask


class ExtractUsernamesJob(BaseJob):
    name = "extract_usernames_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        db_chats = db.graph.get_chats_sorted_by_username_extractor_score()

        for chat in db_chats:
            logger.debug(chat.username)
            # todo: blocking or non-blocking? which one is better suited for this case?
            ExtractUsernamesTask(
                kwargs={
                    "chat": chat,
                }
            ).publish()
