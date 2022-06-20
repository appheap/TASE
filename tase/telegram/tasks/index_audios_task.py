from dataclasses import field, dataclass

from .base_task import BaseTask, exception_handler
from ..telegram_client import TelegramClient
from ...db import DatabaseClient
from ...my_logger import logger


@dataclass
class IndexAudiosTask(BaseTask):
    name: str = field(default="index_audios_task")

    @exception_handler
    def run_task(self, telegram_client: "TelegramClient", db: "DatabaseClient"):
        chat_id = self.kwargs.get("chat_id", None)
        if chat_id is None:
            return

        # todo: retrieve the `last_offset_id` of the chat from database

        try:
            tg_user = telegram_client.get_me()
            tg_chat = telegram_client.get_chat(chat_id=chat_id)
        except ValueError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        else:
            creator = db.update_or_create_user(tg_user)
            chat = db.update_or_create_chat(tg_chat, creator)

            last_offset_id = 1

            for message in telegram_client.iter_audios(
                chat_id=chat_id, offset_id=last_offset_id, only_newer_messages=True
            ):
                db.update_or_create_audio(message, telegram_client.telegram_id)

                if message.id > last_offset_id:
                    last_offset_id = message.id

            # todo: update the `last_offset_id` of the chat in the database
