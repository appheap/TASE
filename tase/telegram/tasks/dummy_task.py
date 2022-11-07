import asyncio

from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient
from tase.telegram.client.client_worker import RabbitMQConsumer


class DummyTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.DUMMY_TASK

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        self.task_in_worker(db)

        logger.info(f"Running Dummy Task with client: {0}")
        # logger.info(f"Running Dummy Task with client: {telegram_client.name}")
        logger.info(f"{self.type.value} : {self.kwargs}")
        logger.info("")
        await asyncio.sleep(1)
        logger.info(f"Finished Dummy Task with client: {0}")
        # logger.info(f"Finished Dummy Task with client: {telegram_client.name}")
        logger.info(f"{self.type.value} : {self.kwargs}")
        logger.info("")

        self.task_done(db)
