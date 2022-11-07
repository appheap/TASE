import asyncio
import pickle
import random
from typing import List, Optional

import aio_pika
from decouple import config

from tase import task_globals
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.rabbimq_consumer import RabbitMQConsumer
from tase.telegram.client import TelegramClient


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
                    asyncio.create_task(body.run(self, self.db, random.choice(self.telegram_clients)))
            else:
                # todo: unknown type for body detected, what now?
                raise TypeError(f"Unknown type for `body`: {type(body)}")
