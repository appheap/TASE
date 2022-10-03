import kombu
from decouple import config
from kombu.entity import TRANSIENT_DELIVERY_MODE

from tase.scheduler.jobs import BaseJob
from tase.telegram.client.tasks.base_task import BaseTask
from tase.telegram.client.worker_commands import BaseWorkerCommand

tase_telegram_exchange = kombu.Exchange(
    "tase_telegram_exchange",
    "direct",
    durable=False,
)

client_worker_controller_broadcast_exchange = kombu.Exchange(
    "client_worker_controller_broadcast_exchange",
    "fanout",
    durable=False,
)

# this queue is for distributing general tasks among all client workers
telegram_workers_general_task_queue = kombu.Queue(
    "telegram_workers_general_task_queue",
    exchange=tase_telegram_exchange,
    routing_key="tase_telegram_queue",
    auto_delete=True,
)
callback_queue = kombu.Queue(
    kombu.uuid(),
    auto_delete=True,
)

scheduler_queue = kombu.Queue(
    f"scheduler_queue",
    exchange=tase_telegram_exchange,
    routing_key="scheduler_queue",
    auto_delete=True,
)

kombu.enable_insecure_serializers()


def publish_client_task(
    task: BaseTask,
    target_queue: kombu.Queue = None,
) -> None:
    """
    Publishes a task on a queue to be executed by a Telegram Client

    Parameters
    ----------
    task : tase.telegram.tasks.BaseTask
        Task to be executed
    target_queue : kombu.Queue
        Queue to send to task to. If no queue is provided, then the task will be broadcasted to all available workers
        and only one of them will process this task.
    """
    if target_queue is None:
        target_queue = telegram_workers_general_task_queue

    publish(task, target_queue)


def publish_job_to_scheduler(job: BaseJob) -> None:
    """
    Publishes a job on the global scheduler queue to be scheduled

    Parameters
    ----------
    job : tase.telegram.jobs.BaseJob
        Job to be scheduled
    """
    publish(job, scheduler_queue)


def broadcast_worker_command_task(
    task: BaseWorkerCommand,
) -> None:
    """
    Broadcasts a command on a queue to be executed by all consumers.

    Parameters
    ----------
    task : tase.telegram.client.worker_commands.BaseWorkerCommand
        Command to be executed
    """
    publish(task, exchange=client_worker_controller_broadcast_exchange)


def publish(
    body: object,
    target_queue: kombu.Queue = None,
    exchange: kombu.Exchange = None,
) -> None:
    """
    Publishes an object on a queue to be processed

    Parameters
    ----------
    body : object
        Object to be sent as input for the worker to process
    target_queue : kombu.Queue
        Queue to send the body to
    exchange : kombu.Exchange
        Exchange to send the body to
    """
    if target_queue is None and exchange is None:
        raise Exception(
            "Both `target_queue` and `exchange` cannot be None at the same time"
        )

    if target_queue is not None and exchange is not None:
        raise Exception(
            "Both `target_queue` and `exchange` cannot be set at the same time"
        )

    routing_key = "" if exchange else target_queue.routing_key
    exchange_ = tase_telegram_exchange if not exchange else exchange
    priority = 0 if not exchange else 9
    declare = [target_queue] if target_queue else []

    with kombu.Connection(
        config("RABBITMQ_URL"),
        userid=config("RABBITMQ_DEFAULT_USER"),
        password=config("RABBITMQ_DEFAULT_PASS"),
    ) as conn:
        # produce
        producer = conn.Producer(serializer="pickle")
        producer.publish(
            body=body,
            delivery_mode=TRANSIENT_DELIVERY_MODE,
            exchange=exchange_,
            routing_key=routing_key,
            declare=declare,
            retry=True,
            priority=priority,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 30,
                "max_retries": 30,
            },
        )
