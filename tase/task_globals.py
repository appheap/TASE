import kombu

kombu.enable_insecure_serializers()

telegram_client_worker_exchange = kombu.Exchange(
    "telegram_client_worker_exchange",
    "direct",
    durable=False,
)

scheduler_exchange = kombu.Exchange(
    "scheduler_exchange",
    "direct",
    durable=False,
)

rabbitmq_worker_command_exchange = kombu.Exchange(
    "rabbitmq_worker_command_exchange",
    "fanout",
    durable=False,
)

# this queue is for distributing general tasks among all client workers
telegram_workers_general_task_queue = kombu.Queue(
    "telegram_workers_general_task_queue",
    exchange=telegram_client_worker_exchange,
    routing_key="tase_telegram_queue",
    auto_delete=True,
)

scheduler_queue = kombu.Queue(
    f"scheduler_queue",
    exchange=scheduler_exchange,
    routing_key="scheduler_queue",
    auto_delete=True,
)
