from threading import Thread
from typing import Dict
from typing import List

import kombu
from kombu import Connection, Queue, Consumer
from kombu.mixins import ConsumerProducerMixin
from kombu.transport import pyamqp

from tase.my_logger import logger
from . import TelegramClient
from .globals import *
from ..db.database_client import DatabaseClient


class ClientTaskConsumer(ConsumerProducerMixin):
    def __init__(
            self,
            connection: 'Connection',
            telegram_client: 'TelegramClient',
            db,
            task_queues: Dict['str', 'kombu.Queue'],
    ):
        logger.info('client task consumer started...')
        self.connection = connection
        self.telegram_client = telegram_client
        self.db = db
        self.task_queues = task_queues

        task_queue = Queue(
            f'{self.telegram_client.get_session_name()}_queue',
            exchange=tase_telegram_exchange,
            routing_key=f'{self.telegram_client.get_session_name()}_queue',
        )
        self.task_queue = task_queue
        self.task_queues[self.telegram_client.get_session_name()] = task_queue
        logger.info(f"task_queues: {self.task_queues}")

    def get_consumers(self, consumer, channel) -> List[Consumer]:
        return [
            Consumer(
                queues=[self.task_queue],
                callbacks=[self.on_task],
                channel=channel,
                prefetch_count=1,
                accept=['pickle'],
                # accept=['json', 'pickle'],
            )
        ]

    def on_task(self, body: dict, message: pyamqp.Message):
        attr_name = body['func']
        args = body['args']
        kwargs = body['kwargs']
        logger.info(f"client_task_consumer_on_task : {self.telegram_client.get_session_name()}")

        response = {}
        if self.telegram_client.is_connected() and attr_name:
            logger.info(attr_name)
            response['result'] = self.telegram_client.get_me()

        self.producer.publish(
            body=response,
            exchange='',
            routing_key=message.properties['reply_to'],
            correlation_id=message.properties['correlation_id'],
            serializer='pickle',
            retry=True,
        )
        message.ack()


class ClientWorkerThread(Thread):

    def __init__(
            self,
            telegram_client: 'TelegramClient',
            index: int, db: 'DatabaseClient',
            task_queues: Dict['str', 'kombu.Queue']
    ):
        super().__init__()
        self.daemon = True
        self.telegram_client = telegram_client
        self.name = f'Client_Worker_Thread {index}'
        self.index = index
        self.db = db
        self.task_queues = task_queues
        self.consumer = None

    def run(self) -> None:
        logger.info(f"Client Worker {self.index} started ....")
        self.consumer = ClientTaskConsumer(
            connection=Connection('amqp://localhost'),
            telegram_client=self.telegram_client,
            db=self.db,
            task_queues=self.task_queues,
        )
        self.consumer.run()
