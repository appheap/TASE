import apscheduler.triggers.interval
import arrow

import tase
from tase import tase_globals
from tase.telegram.client.tasks import CheckUsernamesTask
from .base_job import BaseJob


class CheckUsernamesJob(BaseJob):
    name = "check_usernames_job"
    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+20).datetime,
    )

    def run_job(
        self,
        db: "tase.db.DatabaseClient",
    ) -> None:
        db_usernames = db.get_unchecked_usernames()

        for db_username in db_usernames:
            # todo: blocking or non-blocking? which one is better suited for this case?
            tase_globals.publish_client_task(
                CheckUsernamesTask(
                    kwargs={
                        "db_username": db_username,
                    }
                ),
            )
