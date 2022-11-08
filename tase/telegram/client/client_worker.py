import asyncio
import pickle
import random
from itertools import chain
from typing import List, Dict

import aio_pika
from decouple import config
from pydantic import Field

from tase import task_globals
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.rabbimq_consumer import RabbitMQConsumer
from tase.telegram.client import TelegramClient


class TelegramClientConsumer(RabbitMQConsumer):
    users: Dict[str, TelegramClient] = Field(default={})
    bots: Dict[str, TelegramClient] = Field(default={})

    class Config:
        arbitrary_types_allowed = True

    async def init_rabbitmq_consumer(
        self,
        users: List[TelegramClient],
        bots: List[TelegramClient],
    ):
        for user in users:
            self.users[user.name] = user

        for bot in bots:
            self.bots[bot.name] = bot

        connection = await aio_pika.connect_robust(
            login=config("RABBITMQ_DEFAULT_USER"),
            password=config("RABBITMQ_DEFAULT_PASS"),
        )
        self.connection = connection

        # Creating channel
        channel = await connection.channel()

        # Maximum message count which will be processing at the same time.
        await channel.set_qos(prefetch_count=len(self.users) + len(self.bots))

        # Declaring queue
        for telegram_client in chain(self.users.values(), self.bots.values()):
            queue = await channel.declare_queue(
                f"{telegram_client.name}_task_queue",
                auto_delete=True,
                exclusive=True,
            )
            exchange = await channel.declare_exchange(
                task_globals.telegram_client_worker_exchange.name,
                task_globals.telegram_client_worker_exchange.type,
                durable=task_globals.telegram_client_worker_exchange.durable,
                auto_delete=task_globals.telegram_client_worker_exchange.auto_delete,
            )

            await queue.bind(
                exchange,
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
        exchange = await channel.declare_exchange(
            task_globals.rabbitmq_worker_command_exchange.name,
            task_globals.rabbitmq_worker_command_exchange.type,
            durable=task_globals.rabbitmq_worker_command_exchange.durable,
            auto_delete=task_globals.rabbitmq_worker_command_exchange.auto_delete,
        )

        await queue.bind(
            exchange,
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
        exchange = await channel.declare_exchange(
            task_globals.telegram_client_worker_exchange.name,
            task_globals.telegram_client_worker_exchange.type,
            durable=task_globals.telegram_client_worker_exchange.durable,
            auto_delete=task_globals.telegram_client_worker_exchange.auto_delete,
        )

        await queue.bind(
            exchange,
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
                logger.info(f"TelegramClientConsumer got a new task: {body.type.value}")
                if body.type != RabbitMQTaskType.UNKNOWN:
                    # await body.run(self.db, None)
                    from tase.task_distribution import TargetWorkerType

                    if body.target_worker_type == TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK:
                        asyncio.create_task(
                            body.run(
                                self,
                                self.db,
                                random.choice(list(self.users.values())),
                            )
                        )
                    elif body.target_worker_type == TargetWorkerType.ONE_TELEGRAM_CLIENT_CONSUMER_WORK:
                        if self.users.get(message.routing_key, None):
                            asyncio.create_task(
                                body.run(
                                    self,
                                    self.db,
                                    self.users[message.routing_key],
                                )
                            )
                        else:
                            logger.error(f"Could not find Telegram user client with `{message.routing_key}` name")
                    elif body.target_worker_type == TargetWorkerType.RABBITMQ_CONSUMER_COMMAND:
                        asyncio.create_task(
                            body.run(
                                self,
                                self.db,
                                random.choice(list(self.users.values())),
                            )
                        )
                    else:
                        logger.error(f"Unexpected target_worker_type: `{body.target_worker_type}`")

            else:
                # todo: unknown type for body detected, what now?
                raise TypeError(f"Unknown type for `body`: {type(body)}")
