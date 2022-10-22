from itertools import chain

import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.telegram.tasks import IndexAudiosTask
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...my_logger import logger
from ...telegram.client import TelegramClient


class IndexAudiosJob(BaseJob):
    type = RabbitMQTaskType.INDEX_AUDIOS_JOB
    priority = 3

    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(minutes=+10).datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        self.task_in_worker(db)

        chats = db.graph.get_chats_sorted_by_audio_indexer_score(
            filter_by_indexed_chats=True,
        )
        not_indexed_chats = db.graph.get_chats_sorted_by_audio_indexer_score(
            filter_by_indexed_chats=False,
        )

        # todo: blocking or non-blocking? which one is better suited for this case?
        for chat in chain(chats, not_indexed_chats):
            logger.debug(f"published task for indexing: {chat.username}")
            IndexAudiosTask(
                kwargs={
                    "chat_key": chat.key,
                }
            ).publish(db)

        self.task_done(db)
