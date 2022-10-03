import apscheduler.triggers.interval
import arrow

import tase
from tase.my_logger import logger
from tase.task_distribution import task_globals
from tase.telegram.client.tasks import ExtractUsernamesTask
from .base_job import BaseJob


class ExtractUsernamesJob(BaseJob):
    name = "extract_usernames_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run_job(
        self,
        db: tase.db.DatabaseClient,
    ) -> None:
        db_chats = db.graph.get_chats_sorted_by_username_extractor_score()

        for chat in db_chats:
            logger.debug(chat.username)
            # todo: blocking or non-blocking? which one is better suited for this case?
            task_globals.publish_client_task(
                ExtractUsernamesTask(
                    kwargs={
                        "chat": chat,
                    }
                ),
            )
