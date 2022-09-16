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
        db: tase.db.DatabaseClient,
    ) -> None:
        usernames = db.graph.get_unchecked_usernames()

        for username in usernames:
            # todo: blocking or non-blocking? which one is better suited for this case?
            tase_globals.publish_client_task(
                CheckUsernamesTask(
                    kwargs={
                        "username": username,
                    }
                ),
            )
