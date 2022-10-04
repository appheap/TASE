from enum import Enum


class RabbitMQTaskStatus(Enum):
    UNKNOWN = 0
    CREATED = 1
    IN_QUEUE = 2
    IN_WORKER = 3
    DONE = 4
    CANCELED = 5
    DELETED = 6
    FAILED = 7
