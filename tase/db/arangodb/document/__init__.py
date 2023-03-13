from .audio import Audio, AudioMethods
from .base_document import BaseDocument
from .bot_task import BotTask, BotTaskMethods
from .downloaded_thumbnail_file import DownloadedThumbnailFile, DownloadedThumbnailFileMethods
from .job import Job, JobMethods
from .rabbitmq_task import RabbitMQTask, RabbitMQTaskMethods
from .thumbnail import Thumbnail, ThumbnailMethods


class ArangoDocumentMethods(
    AudioMethods,
    BotTaskMethods,
    DownloadedThumbnailFileMethods,
    JobMethods,
    RabbitMQTaskMethods,
    ThumbnailMethods,
):
    pass


document_classes = [
    Audio,
    BotTask,
    DownloadedThumbnailFile,
    Job,
    RabbitMQTask,
    Thumbnail,
]
