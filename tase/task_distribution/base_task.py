import pickle
from typing import Optional, Tuple

import aio_pika
from decouple import config
from pydantic import BaseModel, Field

from tase.db import DatabaseClient
from .target_worker_type import TargetWorkerType
from .. import task_globals
from ..common.utils import check_ram_usage
from ..db.arangodb.enums import RabbitMQTaskType, RabbitMQTaskStatus
from ..my_logger import logger
from ..task_globals import MyExchange
from ..telegram.client.client_worker import RabbitMQConsumer


class BaseTask(BaseModel):
    target_worker_type: TargetWorkerType
    type: RabbitMQTaskType

    kwargs: dict = Field(default_factory=dict)

    task_key: Optional[str]
    priority: int = Field(default=1)

    async def publish(
        self,
        db: DatabaseClient,
        target_queue_routing_key: str = None,
        priority: int = None,
        check_memory_usage: bool = True,
    ) -> Tuple[Optional[RabbitMQTaskStatus], bool]:
        """
        Publish this task on a queue to be processed

        Parameters
        ----------
        db : DatabaseClient
            Database Client
        target_queue_routing_key : str
            Queue routing key to send the body to
        priority : int, default : None
            Priority of this task on the queue
        check_memory_usage : bool, default : True
            Whether to check for memory usage before publishing the task or not

        Returns
        -------
        tuple of RabbitMQTaskStatus and bool
            Status of the published task and whether the task was created or not. If there was any error in creating the task on the DB, the returned status
            will be None.

        Raises
        ------
        ValueError
            In case the `exchange` parameter is None
        NotEnoughRamError
            In case the there is not enough RAM to execute this task

        """
        if db is None or self.target_worker_type == TargetWorkerType.UNKNOWN or self.type == RabbitMQTaskType.UNKNOWN:
            return None, False

        state_dict = self.kwargs if len(self.kwargs) else None
        active_task = db.document.get_active_rabbitmq_task(
            self.type,
            state_dict,
        )
        status = None
        created = False
        if active_task is None:
            new_task = db.document.create_rabbitmq_task(
                self.type,
                state_dict,
            )
            if new_task:
                self.task_key = new_task.key
            else:
                raise Exception("could not create `RabbitMQTask` document")

            priority = priority if priority is not None else self.priority

            try:
                if self.target_worker_type == TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK:
                    await self._publish_task(
                        task_globals.telegram_workers_general_task_queue_name,
                        task_globals.telegram_client_worker_exchange,
                        priority,
                        check_memory_usage,
                    )
                elif self.target_worker_type == TargetWorkerType.ONE_TELEGRAM_CLIENT_CONSUMER_WORK:
                    await self._publish_task(
                        target_queue_routing_key,
                        task_globals.telegram_client_worker_exchange,
                        priority,
                        check_memory_usage,
                    )
                elif self.target_worker_type == TargetWorkerType.RABBITMQ_CONSUMER_COMMAND:
                    await self._publish_task(
                        None,
                        task_globals.rabbitmq_worker_command_exchange,
                        priority,
                        check_memory_usage,
                    )
                elif self.target_worker_type == TargetWorkerType.SCHEDULER_JOB:
                    await self._publish_task(
                        task_globals.scheduler_queue_name,
                        task_globals.scheduler_exchange,
                        priority,
                        check_memory_usage,
                    )
            except Exception as e:
                logger.exception(e)
                new_task.update_status(RabbitMQTaskStatus.FAILED)
            else:
                new_task.update_status(RabbitMQTaskStatus.IN_QUEUE)

            status = new_task.status
            created = True

        else:
            status = active_task.status
            created = False

        return status, created

    async def _publish_task(
        self,
        target_queue_name: str = None,
        exchange: MyExchange = None,
        priority: int = 1,
        check_memory_usage: bool = True,
    ):
        """
        Publishes an object on a queue to be processed

        Parameters
        ----------
        target_queue_name : str
            Queue name to send the body to
        exchange : MyExchange
            Exchange to send the body to
        priority : int, default : 1
            Priority of this task on the queue
        check_memory_usage: bool, default : True
            Whether to check for memory usage before publishing the task or not

        Raises
        ------
        ValueError
            In case the `exchange` parameter is None
        NotEnoughRamError
            In case the RAM usage is greater than given threshold
        """
        if exchange is None:
            raise ValueError("Parameter `exchange` cannot be `None`")

        if check_memory_usage:
            check_ram_usage()

        routing_key = ""
        if exchange and target_queue_name:
            routing_key = target_queue_name

        connection = await aio_pika.connect_robust(
            login=config("RABBITMQ_DEFAULT_USER"),
            password=config("RABBITMQ_DEFAULT_PASS"),
        )

        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                exchange.name,
                exchange.type,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
                passive=True,
            )
            # exchange=await channel.get_exchange(exchange.name)

            await exchange.publish(
                aio_pika.Message(
                    body=pickle.dumps(self),
                    priority=priority,
                ),
                routing_key=routing_key,
            )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        raise NotImplementedError

    def task_in_worker(
        self,
        db: DatabaseClient,
    ) -> bool:
        task = db.document.get_rabbitmq_task_by_key(self.task_key)
        if task:
            return task.update_status(RabbitMQTaskStatus.IN_WORKER)

        return False

    def task_done(
        self,
        db: DatabaseClient,
    ) -> bool:
        task = db.document.get_rabbitmq_task_by_key(self.task_key)
        if task:
            return task.update_status(RabbitMQTaskStatus.DONE)

        return False

    def task_failed(
        self,
        db: DatabaseClient,
    ) -> bool:
        task = db.document.get_rabbitmq_task_by_key(self.task_key)
        if task:
            return task.update_status(RabbitMQTaskStatus.FAILED)

        return False
