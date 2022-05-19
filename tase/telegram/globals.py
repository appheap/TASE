import kombu
from kombu import Connection, Exchange, Queue, uuid

from tase.my_logger import logger
from tase.telegram.tasks.base_task import BaseTask
from tase.utils import prettify
from decouple import config

tase_telegram_exchange = Exchange('tase_telegram_exchange', 'direct', durable=True)
tase_telegram_queue = Queue('tase_telegram_queue', exchange=tase_telegram_exchange, routing_key='tase_telegram_queue')
callback_queue = Queue(uuid(), auto_delete=True)

kombu.enable_insecure_serializers()


def client_task(task: BaseTask, target_queue: 'Queue'):
    logger.info(f"@pyrogram_task_call: {prettify(task)}")

    # connections
    with Connection(
            config('RABBITMQ_URL'),
            userid=config('RABBITMQ_DEFAULT_USER'),
            password=config('RABBITMQ_DEFAULT_PASS'),
    ) as conn:
        # produce
        producer = conn.Producer(serializer='pickle')
        producer.publish(body=task,
                         exchange=tase_telegram_exchange,
                         routing_key=target_queue.name,
                         declare=[target_queue, ],
                         retry=True,
                         retry_policy={
                             'interval_start': 0,
                             'interval_step': 2,
                             'interval_max': 30,
                             'max_retries': 30,
                         })
