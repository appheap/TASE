from .audio import Audio, AudioMethods
from .base_document import BaseDocument
from .bot_task import BotTask, BotTaskMethods
from .downloaded_thumbnail_file import DownloadedThumbnailFile, DownloadedThumbnailFileMethods
from .job import Job, JobMethods
from .rabbitmq_task import RabbitMQTask, RabbitMQTaskMethods
from .uploaded_thumbnail_file import UploadedThumbnailFile, UploadedThumbnailFileMethods


class ArangoDocumentMethods(
    AudioMethods,
    BotTaskMethods,
    DownloadedThumbnailFileMethods,
    JobMethods,
    RabbitMQTaskMethods,
    UploadedThumbnailFileMethods,
):
    pass


document_classes = [
    Audio,
    BotTask,
    DownloadedThumbnailFile,
    Job,
    RabbitMQTask,
    UploadedThumbnailFile,
]
