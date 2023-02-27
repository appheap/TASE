from .audio import Audio, AudioMethods
from .base_document import BaseDocument
from .bot_task import BotTask, BotTaskMethods
from .job import Job, JobMethods
from .rabbitmq_task import RabbitMQTask, RabbitMQTaskMethods
from .thumbnail import Thumbnail, ThumbnailMethods


class ArangoDocumentMethods(
    AudioMethods,
    BotTaskMethods,
    JobMethods,
    RabbitMQTaskMethods,
    ThumbnailMethods,
):
    pass


document_classes = [
    Audio,
    BotTask,
    Job,
    RabbitMQTask,
    Thumbnail,
]
