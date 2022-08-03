import apscheduler.triggers.base
import kombu
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
from kombu import Connection, Exchange, Queue, uuid

import tase
from tase.my_logger import logger
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

kombu.enable_insecure_serializers()


def publish_client_task(
    task: BaseTask,
    target_queue: kombu.Queue,
) -> None:
    """
    Publishes a task to a queue to be executed by a Telegram Client

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


def job(*args, **kwargs) -> None:
    """
    This functions serves as wrapper for RabbitMQ Tasks to be scheduled using APScheduler.

    Parameters
    ----------
    args : tuple
        A list of arguments provided as input to the job. The first argument is a subclass of
        `BaseTask<tase.telegram.tasks.BaseTask>` and second argument is the queue (instance of `Queue<kombu.Queue>`
        class) which task will be sent to.
    kwargs : dict
        A dictionary containing other keyword arguments passed to this function.
    """
    publish_client_task(
        args[0],
        target_queue=args[1],
    )


def add_job(
    task: BaseTask,
    queue: kombu.Queue,
    trigger: apscheduler.triggers.base.BaseTrigger,
    telegram_client: "tase.telegram.TelegramClient",
) -> None:
    """
    Adds a job to the scheduler to be scheduled to run based on the type of the trigger provided.

    Parameters
    ----------

    task : tase.telegram.tasks.BaseTask
        Task to be scheduled
    queue : kombu.Queue
        Queue to send the task to be executed on
    trigger : apscheduler.triggers.base.BaseTrigger
        Trigger that determines when the job is executed
    telegram_client : tase.telegram.TelegramClient
        Telegram client who added the job

    """

    if telegram_client.scheduler is None:
        # fixme: use a global scheduler for all telegram clients instead
        telegram_client.scheduler = BackgroundScheduler()
        telegram_client.scheduler.start()


    telegram_client.scheduler.add_job(
        job,
        trigger,
        args=[
            task,
            queue,
        ],
        kwargs={},
    )
