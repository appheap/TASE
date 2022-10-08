import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.my_logger import logger
from tase.telegram.tasks import ExtractUsernamesTask
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...telegram.client import TelegramClient


class ExtractUsernamesJob(BaseJob):
    type = RabbitMQTaskType.EXTRACT_USERNAMES_JOB

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
        self.task_in_worker(db)
        db_chats = db.graph.get_chats_sorted_by_username_extractor_score()

        for chat in db_chats:
            logger.debug(chat.username)
            # todo: blocking or non-blocking? which one is better suited for this case?
            ExtractUsernamesTask(
                kwargs={
                    "chat_key": chat.key,
                }
            ).publish(db)

        self.task_done(db)
