from kombu import Connection, Exchange, Queue, uuid, Consumer

from tase.my_logger import logger
from tase.utils import prettify

tase_telegram_exchange = Exchange('tase_telegram_exchange', 'direct', durable=True)
tase_telegram_queue = Queue('tase_telegram_queue', exchange=tase_telegram_exchange, routing_key='tase_telegram_queue')
callback_queue = Queue(uuid(), auto_delete=True)

number_of_telegram_workers = 5


def client_task(func_body, target_queue: 'Queue'):
    logger.info(f"@pyrogram_task_call: {prettify(func_body)}")

    response = None

    def callback(body, message):
        nonlocal response
        response = body
        logger.info(f"@pyrogram_task_response: {body} ")

    # connections
    with Connection('amqp://localhost') as conn:
        # produce
        producer = conn.Producer(serializer='pickle')
        producer.publish(body=func_body,
                         exchange=tase_telegram_exchange,
                         routing_key=target_queue.name,
                         declare=[target_queue, callback_queue],
                         retry=True,
                         correlation_id=uuid(),
                         reply_to=callback_queue.name,
                         retry_policy={
                             'interval_start': 0,
                             'interval_step': 2,
                             'interval_max': 30,
                             'max_retries': 30,
                         })
        with Consumer(conn, callbacks=[callback], queues=[callback_queue], no_ack=True):
            while response is None:
                conn.drain_events()
    return response
