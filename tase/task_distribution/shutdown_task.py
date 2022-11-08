from tase.db import DatabaseClient
from tase.telegram.client import TelegramClient
from .base_task import BaseTask
from .target_worker_type import TargetWorkerType
from ..db.arangodb.enums import RabbitMQTaskType
from ..telegram.client.client_worker import RabbitMQConsumer


class ShutdownTask(BaseTask):
    target_worker_type = TargetWorkerType.RABBITMQ_CONSUMER_COMMAND
    type = RabbitMQTaskType.SHUTDOWN_TASK
    priority = 10

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        self.task_in_worker(db)
        await consumer.shutdown()

        from tase.scheduler.scheduler import SchedulerJobConsumer

        if isinstance(consumer, SchedulerJobConsumer):
            if consumer.scheduler.running:
                consumer.scheduler.shutdown()

        # todo: add more functionality to this command. for instance, wrap the tasks in queue in a job and schedule
        #  them for the next consumer start/restart.
        self.task_done(db)
