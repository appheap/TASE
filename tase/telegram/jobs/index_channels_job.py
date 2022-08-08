import apscheduler.triggers.interval
import arrow

import tase
from .base_job import BaseJob
from ..tasks import IndexAudiosTask
from ...my_logger import logger


class IndexChannelsJob(BaseJob):
    name = "index_channels_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+30).datetime,
    )

    def run_job(
        self,
        db: "tase.db.DatabaseClient",
    ) -> None:
        from ..globals import publish_client_task

        db_chats = db.get_chats_sorted_by_audio_indexer_score()

        # fixme: remove this later
        logger.debug([chat.username for chat in db_chats])

        # todo: blocking or non-blocking? which one is better suited for this case?
        for db_chat in db_chats:
            publish_client_task(
                IndexAudiosTask(
                    kwargs={
                        "db_chat": db_chat,
                    }
                ),
            )
