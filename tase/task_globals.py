from aio_pika import ExchangeType
from pydantic import BaseModel


class MyExchange(BaseModel):
    name: str
    type: ExchangeType
    durable: bool
    auto_delete: bool


class TelegramClientWorkerExchange(MyExchange):
    name = "telegram_client_worker_exchange"
    type = ExchangeType.DIRECT
    durable = False
    auto_delete = True


class SchedulerExchange(MyExchange):
    name = "scheduler_exchange"
    type = ExchangeType.DIRECT
    durable = False
    auto_delete = True


class RabbitMQWorkerCommandExchange(MyExchange):
    name = "rabbitmq_worker_command_exchange"
    type = ExchangeType.FANOUT
    durable = False
    auto_delete = True


telegram_client_worker_exchange = TelegramClientWorkerExchange()
scheduler_exchange = SchedulerExchange()
rabbitmq_worker_command_exchange = RabbitMQWorkerCommandExchange()

# this queue is for distributing general tasks among all client workers
telegram_workers_general_task_queue_name = "telegram_workers_general_task_queue"

scheduler_queue_name = "scheduler_queue"
