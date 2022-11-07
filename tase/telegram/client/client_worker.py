import asyncio
import pickle
from threading import Thread
from typing import Dict, List, Optional

import aio_pika
import kombu
from decouple import config
from kombu import Consumer, Queue, Connection
from kombu.mixins import ConsumerProducerMixin
from kombu.transport import pyamqp

from tase import task_globals
from tase.common.utils import sync_exception_handler
from tase.configs import ClientTypes
from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.rabbimq_consumer import RabbitMQConsumer
from tase.telegram.client import TelegramClient


class ClientTaskConsumer(ConsumerProducerMixin):
    def __init__(
        self,
        connection: Connection,
        telegram_client: TelegramClient,
        db,
        client_worker_queues: Dict[str, kombu.Queue],
    ):
        logger.info("client task consumer started...")
        self.connection = connection
        self.telegram_client = telegram_client
        self.db = db
        self.client_worker_queues = client_worker_queues

        telegram_client_worker_task_queue = Queue(
            f"{self.telegram_client.get_session_name()}_task_queue",
            exchange=task_globals.telegram_client_worker_exchange,
            routing_key=f"{self.telegram_client.get_session_name()}_task_queue",
            auto_delete=True,
        )
        self.telegram_client_worker_task_queue = telegram_client_worker_task_queue
        self.client_worker_queues[self.telegram_client.name] = telegram_client_worker_task_queue
        logger.info(f"client_worker_queues: {self.client_worker_queues}")

        rabbitmq_worker_command_queue = Queue(
            f"{self.telegram_client.get_session_name()}_command_queue",
            exchange=task_globals.rabbitmq_worker_command_exchange,
            routing_key=f"{self.telegram_client.get_session_name()}_command_queue",
            auto_delete=True,
        )
        self.rabbitmq_worker_command_queue = rabbitmq_worker_command_queue

    def get_consumers(
        self,
        consumer,
        channel,
    ) -> List[Consumer]:
        if self.telegram_client.client_type == ClientTypes.USER:
            return [
                Consumer(
                    queues=[self.rabbitmq_worker_command_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
                Consumer(
                    queues=[self.telegram_client_worker_task_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
                Consumer(
                    queues=[task_globals.telegram_workers_general_task_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
            ]
        else:
            return [
                Consumer(
                    queues=[self.rabbitmq_worker_command_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
                Consumer(
                    queues=[self.telegram_client_worker_task_queue],
                    callbacks=[self.on_task],
                    channel=channel,
                    prefetch_count=1,
                    accept=["pickle"],
                ),
            ]

    @sync_exception_handler
    def on_task(
        self,
        body: object,
        message: pyamqp.Message,
    ):
        message.ack()

        if self.should_stop:
            return

        from tase.task_distribution import BaseTask

        if isinstance(body, BaseTask):
            logger.info(f"Worker got a new task: {body.type.value} @ {self.telegram_client.get_session_name()}")
            if self.telegram_client.is_connected() and body.type != RabbitMQTaskType.UNKNOWN:
                body.run(self, self.db, self.telegram_client)
        else:
            # todo: unknown type for body detected, what now?
            raise TypeError(f"Unknown type for `body`: {type(body)}")


class ClientWorkerThread(Thread):
    def __init__(
        self,
        telegram_client: TelegramClient,
        index: int,
        db: DatabaseClient,
        client_worker_queues: Dict[str, kombu.Queue],
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


class TelegramClientConsumer(RabbitMQConsumer):
    telegram_clients: Optional[List[TelegramClient]]

    class Config:
        arbitrary_types_allowed = True

    async def init_rabbitmq_consumer(
        self,
        telegram_clients: List[TelegramClient],
    ):
        self.telegram_clients = telegram_clients

        connection = await aio_pika.connect_robust(
            login=config("RABBITMQ_DEFAULT_USER"),
            password=config("RABBITMQ_DEFAULT_PASS"),
        )
        self.connection = connection

        # Creating channel
        channel = await connection.channel()

        # Maximum message count which will be processing at the same time.
        await channel.set_qos(prefetch_count=len(self.telegram_clients))

        # Declaring queue
        for telegram_client in self.telegram_clients:
            queue = await channel.declare_queue(
                f"{telegram_client.name}_task_queue",
                auto_delete=True,
                exclusive=True,
            )

            await queue.bind(
                task_globals.telegram_client_worker_exchange.name,
                routing_key=f"{telegram_client.name}_task_queue",
                robust=True,
            )
            await queue.consume(self.process_message)

        ############################################################

        queue = await channel.declare_queue(
            "telegram_client_manager_command_queue",
            auto_delete=True,
            exclusive=True,
        )

        await queue.bind(
            task_globals.rabbitmq_worker_command_exchange.name,
            routing_key="telegram_client_manager_command_queue",
            robust=True,
        )
        await queue.consume(self.process_message)

        ############################################################

        # Declaring queue
        queue = await channel.declare_queue(
            task_globals.telegram_workers_general_task_queue_name,
            auto_delete=True,
            exclusive=True,
        )

        await queue.bind(
            task_globals.telegram_client_worker_exchange.name,
            routing_key=task_globals.telegram_workers_general_task_queue_name,
            robust=True,
        )
        await queue.consume(self.process_message)

    async def shutdown(self):
        if self.connection is not None:
            await self.connection.close()

    async def process_message(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            from tase.task_distribution import BaseTask

            body = pickle.loads(message.body)

            if isinstance(body, BaseTask):
                logger.info(f"Worker got a new task: {body.type.value} @ {0}")
                if body.type != RabbitMQTaskType.UNKNOWN:
                    # await body.run(self.db, None)
                    asyncio.create_task(body.run(self, self.db, None))
            else:
                # todo: unknown type for body detected, what now?
                raise TypeError(f"Unknown type for `body`: {type(body)}")
