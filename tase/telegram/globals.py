import kombu
from decouple import config
from kombu import Connection, Exchange, Queue, uuid

import tase
from tase.my_logger import logger
from tase.telegram.jobs import BaseJob
from tase.telegram.tasks.base_task import BaseTask
from tase.utils import prettify

tase_telegram_exchange = Exchange(
    "tase_telegram_exchange",
    "direct",
    durable=True,
)

# this queue is for distributing general tasks among all client workers
tase_telegram_queue = Queue(
    "tase_telegram_queue",
    exchange=tase_telegram_exchange,
    routing_key="tase_telegram_queue",
)
callback_queue = Queue(
    uuid(),
    auto_delete=True,
)

scheduler_queue = Queue(
    f"scheduler_queue",
    exchange=tase_telegram_exchange,
    routing_key="scheduler_queue",
)

kombu.enable_insecure_serializers()


def publish_client_task(
    task: BaseTask,
    target_queue: kombu.Queue,
) -> None:
    """
    Publishes a task on a queue to be executed by a Telegram Client

    Parameters
    ----------
    task : tase.telegram.tasks.BaseTask
        Task to be executed
    target_queue : kombu.Queue
        Queue to send to task to
    """
    logger.info(f"@publish_client_task: {prettify(task)}")

    # connections
    with Connection(
        config("RABBITMQ_URL"),
        userid=config("RABBITMQ_DEFAULT_USER"),
        password=config("RABBITMQ_DEFAULT_PASS"),
    ) as conn:
        # produce
        producer = conn.Producer(serializer="pickle")
        producer.publish(
            body=task,
            exchange=tase_telegram_exchange,
            routing_key=target_queue.routing_key,
            declare=[
                target_queue,
            ],
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 30,
                "max_retries": 30,
            },
        )


def publish_job_to_scheduler(job: BaseJob) -> None:
    """
    Publishes a job on the global scheduler queue to be scheduled

    Parameters
    ----------
    job : tase.telegram.jobs.BaseJob
        Job to be scheduled
    """
    logger.info(f"@publish_job_to_scheduler: {prettify(job)}")

    # connections
    with Connection(
        config("RABBITMQ_URL"),
        userid=config("RABBITMQ_DEFAULT_USER"),
        password=config("RABBITMQ_DEFAULT_PASS"),
    ) as conn:
        # produce
        producer = conn.Producer(serializer="pickle")
        producer.publish(
            body=job,
            exchange=tase_telegram_exchange,
            routing_key=scheduler_queue.routing_key,
            declare=[
                scheduler_queue,
            ],
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 30,
                "max_retries": 30,
            },
        )
