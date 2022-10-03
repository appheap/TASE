import arrow
from apscheduler.triggers.interval import IntervalTrigger

from tase.my_logger import logger
from . import BaseJob
from ...db import DatabaseClient


class DummyJob(BaseJob):
    name = "dummy job"
    trigger = IntervalTrigger(
        seconds=5,
        start_date=arrow.now().datetime,
    )

    def run_job(
        self,
        db: DatabaseClient,
    ):
        logger.info(f"{self.name} : {self.kwargs}")
