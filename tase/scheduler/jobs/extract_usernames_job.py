import apscheduler.triggers.interval
import arrow

import tase
from .base_job import BaseJob
from tase.telegram.tasks import ExtractUsernamesTask
from tase.my_logger import logger
from tase import globals

class ExtractUsernamesJob(BaseJob):
    name = "extract_usernames_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run_job(
        self,
        db: "tase.db.DatabaseClient",
    ) -> None:
        db_chats = db.get_chats_sorted_by_username_extractor_score()

        # fixme: remove this later
        logger.debug([chat.username for chat in db_chats])

        for db_chat in db_chats:
            # todo: blocking or non-blocking? which one is better suited for this case?
            globals.publish_client_task(
                ExtractUsernamesTask(
                    kwargs={
                        "db_chat": db_chat,
                    }
                ),
            )
