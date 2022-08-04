from pydantic import Field

from .base_task import BaseTask
from ..telegram_client import TelegramClient
from ...db import DatabaseClient
from ...my_logger import logger
from ...utils import get_timestamp


class IndexAudiosTask(BaseTask):
    name: str = Field(default="index_audios_task")

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
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

            last_offset_id = chat.last_indexed_offset_message_id
            last_offset_date = chat.last_indexed_offset_date

            for message in telegram_client.iter_audios(
                chat_id=chat_id,
                offset_id=last_offset_id,
                only_newer_messages=True,
            ):
                db.update_or_create_audio(
                    message,
                    telegram_client.telegram_id,
                )

                if message.id > last_offset_id:
                    last_offset_id = message.id
                    last_offset_date = get_timestamp(message.date)

            chat.update_offset_attributes(last_offset_id, last_offset_date)
            logger.debug(f"Finished {chat.username}")