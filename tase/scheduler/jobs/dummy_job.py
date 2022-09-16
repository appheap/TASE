from pydantic import Field

from tase.my_logger import logger
from . import BaseJob
from ...db import DatabaseClient


class DummyJob(BaseJob):
    name: str = Field(default="dummy job")

    def run_job(
        self,
        db: DatabaseClient,
    ):
        logger.info(f"{self.name} : {self.kwargs}")
