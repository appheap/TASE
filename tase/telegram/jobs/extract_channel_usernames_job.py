import apscheduler.triggers.interval
import arrow

import tase
from .base_job import BaseJob
from ..tasks import ExtractChannelUserNamesTask
from ...my_logger import logger


class ExtractChannelUserNamesJob(BaseJob):
    name = "extract_channel_usernames_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run_job(
        self,
        db: "tase.db.DatabaseClient",
    ) -> None:
        from ..globals import publish_client_task

        db_chats = db.get_chats_sorted_by_username_extractor_score()

        # fixme: remove this later
        logger.debug([chat.username for chat in db_chats])

        for db_chat in db_chats:
            publish_client_task(
                ExtractChannelUserNamesTask(
                    kwargs={
                        "db_chat": db_chat,
                    }
                ),
            )
