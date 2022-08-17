from .audio import Audio, AudioMethods
from .base_document import BaseDocument
from .bot_task import BotTask, BotTaskMethods


class ArangoDocumentMethods(
    AudioMethods,
    BotTaskMethods,
):
    pass


document_classes = [
    Audio,
    BotTask,
]
