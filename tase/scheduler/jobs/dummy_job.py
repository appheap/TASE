from pydantic import Field

from . import BaseJob
from tase.db import DatabaseClient
from tase.my_logger import logger


class DummyJob(BaseJob):
    name: str = Field(default="dummy job")

    def run_job(
        self,
        db: "DatabaseClient",
    ):
        logger.info(f"{self.name} : {self.kwargs}")
