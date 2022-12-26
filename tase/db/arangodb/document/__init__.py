from .audio import Audio, AudioMethods
from .audio_inline_message import (
    AudioInlineMessage,
    AudioInlineMessageMethods,
)
from .base_document import BaseDocument
from .bot_task import BotTask, BotTaskMethods
from .job import Job, JobMethods
from .playlist_inline_message import PlaylistInlineMessage, PlaylistInlineMessageMethods
from .rabbitmq_task import RabbitMQTask, RabbitMQTaskMethods


class ArangoDocumentMethods(
    AudioMethods,
    AudioInlineMessageMethods,
    BotTaskMethods,
    JobMethods,
    PlaylistInlineMessageMethods,
    RabbitMQTaskMethods,
):
    pass


document_classes = [
    Audio,
    AudioInlineMessage,
    BotTask,
    Job,
    PlaylistInlineMessage,
    RabbitMQTask,
]
