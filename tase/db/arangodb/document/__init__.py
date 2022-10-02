from .audio import Audio, AudioMethods
from .audio_inline_message import (
    AudioInlineMessage,
    AudioInlineMessageMethods,
)
from .base_document import BaseDocument
from .bot_task import BotTask, BotTaskMethods


class ArangoDocumentMethods(
    AudioMethods,
    AudioInlineMessageMethods,
    BotTaskMethods,
):
    pass


document_classes = [
    Audio,
    AudioInlineMessage,
    BotTask,
]
