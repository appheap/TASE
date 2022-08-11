from threading import Thread
from typing import Dict, List

import kombu
from decouple import config
from kombu import Consumer, Queue, Connection
from kombu.mixins import ConsumerProducerMixin
from kombu.transport import pyamqp

from tase import tase_globals
from tase.configs import ClientTypes
from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram.client import TelegramClient
from tase.telegram.client.tasks import BaseTask
from tase.utils import exception_handler


class ClientTaskConsumer(ConsumerProducerMixin):
    def __init__(
        self,
        connection: "Connection",
        telegram_client: "TelegramClient",
        db,
        client_worker_queues: Dict["str", "kombu.Queue"],
    ):
        logger.info("client task consumer started...")
        self.connection = connection
        self.telegram_client = telegram_client
        self.db = db
        self.client_worker_queues = client_worker_queues

        client_worker_private_queue = Queue(
            f"{self.telegram_client.get_session_name()}_queue",
            exchange=tase_globals.tase_telegram_exchange,
            routing_key=f"{self.telegram_client.get_session_name()}_queue",
        )
        self.client_worker_private_queue = client_worker_private_queue
        self.client_worker_queues[self.telegram_client.name] = client_worker_private_queue
        logger.info(f"client_worker_queues: {self.client_worker_queues}")

    def get_consumers(
        self,
        consumer,
        channel,
    ) -> List[Consumer]:
        if self.telegram_client.client_type == ClientTypes.USER:
            return [
                Consumer(
                    queues=[self.client_worker_private_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
                Consumer(
                    queues=[tase_globals.tase_telegram_client_worker_general_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
            ]
        else:
            return [
                Consumer(
                    queues=[self.client_worker_private_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
            ]

    @exception_handler
    def on_task(
        self,
        body: object,
        message: pyamqp.Message,
    ):
        message.ack()

        task: BaseTask = body
        logger.info(f"client_task_consumer_on_task : {self.telegram_client.get_session_name()}")

        if self.telegram_client.is_connected() and task.name:
            task.run_task(self.telegram_client, self.db)


class ClientWorkerThread(Thread):
    def __init__(
        self,
        telegram_client: "TelegramClient",
        index: int,
        db: "DatabaseClient",
        client_worker_queues: Dict["str", "kombu.Queue"],
    ):
        super().__init__()
        self.daemon = True
        self.telegram_client = telegram_client
        self.name = f"Client_Worker_Thread {index}"
        self.index = index
        self.db = db
        self.client_worker_queues = client_worker_queues
        self.consumer = None

    def run(self) -> None:
        logger.info(f"Client Worker {self.index} started ....")
        self.consumer = ClientTaskConsumer(
            connection=Connection(
                config("RABBITMQ_URL"),
                userid=config("RABBITMQ_DEFAULT_USER"),
                password=config("RABBITMQ_DEFAULT_PASS"),
            ),
            telegram_client=self.telegram_client,
            db=self.db,
            client_worker_queues=self.client_worker_queues,
        )
        self.consumer.run()
