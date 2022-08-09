from collections import defaultdict
from typing import Callable, Dict, List, Union

import kombu
from pydantic import BaseModel

from tase.db import elasticsearch_models, graph_models
from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from .handler_metadata import HandlerMetadata
from ...telegram_client import TelegramClient


def exception_handler(func: "Callable"):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrap


class BaseHandler(BaseModel):
    db: "DatabaseClient"
    task_queues: Dict["str", "kombu.Queue"]
    telegram_client: "TelegramClient"

    class Config:
        arbitrary_types_allowed = True

    def init_handlers(self) -> List["HandlerMetadata"]:
        raise NotImplementedError

    def update_audio_cache(
        self,
        db_audios: Union[List[graph_models.vertices.Audio], List[elasticsearch_models.Audio]],
    ) -> Dict[int, graph_models.vertices.Chat]:
        """
        Update Audio file caches that are not been cached by this telegram client

        Parameters
        ----------
        db_audios : Union[List[graph_models.vertices.Audio], List[elasticsearch_models.Audio]]
            List of audios to be checked
        Returns
        -------
        A dictionary mapping from `chat_id` to a Chat object
        """
        chat_msg = defaultdict(list)
        chats_dict = {}
        for db_audio in db_audios:
            if not self.db.get_audio_file_from_cache(db_audio, self.telegram_client.telegram_id):
                chat_msg[db_audio.chat_id].append(db_audio.message_id)

            if not chats_dict.get(db_audio.chat_id, None):
                db_chat = self.db.get_chat_by_chat_id(db_audio.chat_id)

                chats_dict[db_chat.chat_id] = db_chat

        for chat_id, message_ids in chat_msg.items():
            db_chat = chats_dict[chat_id]

            # todo: this approach is only for public channels, what about private channels?
            messages = self.telegram_client.get_messages(chat_id=db_chat.username, message_ids=message_ids)

            for message in messages:
                self.db.update_or_create_audio(
                    message,
                    self.telegram_client.telegram_id,
                )
        return chats_dict
