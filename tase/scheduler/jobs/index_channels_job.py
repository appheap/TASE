import apscheduler.triggers.interval
import arrow

import tase
from tase.my_logger import logger
from tase.task_distribution import task_globals
from tase.telegram.client.tasks import IndexAudiosTask
from .base_job import BaseJob


class IndexChannelsJob(BaseJob):
    name = "index_channels_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+10).datetime,
    )

    def run_job(
        self,
        db: tase.db.DatabaseClient,
    ) -> None:
        chats = db.graph.get_chats_sorted_by_audio_indexer_score()

        # todo: blocking or non-blocking? which one is better suited for this case?
        for chat in chats:
            logger.debug(chat.username)
            task_globals.publish_client_task(
                IndexAudiosTask(
                    kwargs={
                        "chat": chat,
                    }
                ),
            )
