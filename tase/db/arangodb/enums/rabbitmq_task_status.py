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

    def is_active(self) -> bool:
        return (
            True
            if self
            in (
                RabbitMQTaskStatus.CREATED,
                RabbitMQTaskStatus.IN_QUEUE,
                RabbitMQTaskStatus.IN_WORKER,
            )
            else False
        )

    def is_finished(self) -> bool:
        return (
            True
            if self
            in (
                RabbitMQTaskStatus.DONE,
                RabbitMQTaskStatus.CANCELED,
                RabbitMQTaskStatus.DELETED,
                RabbitMQTaskStatus.FAILED,
            )
            else False
        )

    def is_failed(self):
        return self == RabbitMQTaskStatus.FAILED
