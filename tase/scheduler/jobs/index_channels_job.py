import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.my_logger import logger
from tase.telegram.tasks import IndexAudiosTask
from .base_job import BaseJob
from ...telegram.client import TelegramClient


class IndexChannelsJob(BaseJob):
    name = "index_channels_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+10).datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        chats = db.graph.get_chats_sorted_by_audio_indexer_score()

        # todo: blocking or non-blocking? which one is better suited for this case?
        for chat in chats:
            logger.debug(chat.username)
            IndexAudiosTask(
                kwargs={
                    "chat": chat,
                }
            ).publish()
