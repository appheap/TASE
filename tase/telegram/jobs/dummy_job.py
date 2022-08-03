from pydantic import Field

from . import BaseJob
from ...db import DatabaseClient
from ...my_logger import logger


class DummyJob(BaseJob):
    name: str = Field(default="dummy job")

    def run_job(
        self,
        db: "DatabaseClient",
    ):
        logger.info(f"{self.name} : {self.kwargs}")
