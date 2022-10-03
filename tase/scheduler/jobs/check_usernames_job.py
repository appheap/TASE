import arrow
from apscheduler.triggers.interval import IntervalTrigger

import tase
from tase.task_distribution import task_globals
from tase.telegram.client.tasks import CheckUsernamesTask
from .base_job import BaseJob


class CheckUsernamesJob(BaseJob):
    name = "check_usernames_job"
    trigger = IntervalTrigger(
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
            task_globals.publish_client_task(
                CheckUsernamesTask(
                    kwargs={
                        "username": username,
                    }
                ),
            )
