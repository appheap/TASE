from pydantic import Field

from .base_task import BaseTask
from ..telegram_client import TelegramClient
from ...db import DatabaseClient, graph_models
from ...my_logger import logger
from ...utils import get_timestamp


class IndexAudiosTask(BaseTask):
    name: str = Field(default="index_audios_task")

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        db_chat: graph_models.vertices.Chat = self.kwargs.get("db_chat")
        if db_chat is None:
            return

        chat_id = db_chat.username if db_chat.username else db_chat.invite_link
        title = db_chat.title

        try:
            tg_user = telegram_client.get_me()
            tg_chat = telegram_client.get_chat(chat_id)
        except ValueError as e:
            # In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # todo: fix this
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        else:
            creator = db.update_or_create_user(tg_user)
            db_chat = db.update_or_create_chat(tg_chat, creator)

            if creator and db_chat:
                last_offset_id = db_chat.audio_indexer_metadata.last_message_offset_id
                last_offset_date = db_chat.audio_indexer_metadata.last_message_offset_date

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

                db.update_audio_indexer_metadata(db_chat, last_offset_id, last_offset_date)
                logger.debug(f"Finished {title}")
            else:
                logger.debug(f"Error occurred: {title}")
