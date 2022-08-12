from typing import Optional

from pydantic import Field

from tase.db import DatabaseClient, graph_models
from tase.db.graph_models.helper_models import AudioIndexerMetadata
from tase.my_logger import logger
from tase.telegram.client import TelegramClient
from tase.utils import get_timestamp, prettify
from .base_task import BaseTask


class IndexAudiosTask(BaseTask):
    name: str = Field(default="index_audios_task")

    metadata: Optional[AudioIndexerMetadata]

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
                self.metadata = db_chat.audio_indexer_metadata

                for message in telegram_client.iter_messages(
                    chat_id=chat_id,
                    offset_id=self.metadata.last_message_offset_id,
                    only_newer_messages=True,
                    filter="audio",
                ):
                    self.metadata.message_count += 1

                    db.update_or_create_audio(
                        message,
                        telegram_client.telegram_id,
                    )

                    if message.id > self.metadata.last_message_offset_id:
                        self.metadata.last_message_offset_id = message.id
                        self.metadata.last_message_offset_date = get_timestamp(message.date)

                db.update_audio_indexer_metadata(db_chat, self.metadata)
                logger.info(f"{prettify(self.metadata)}")
                logger.debug(f"Finished {title}")
            else:
                logger.debug(f"Error occurred: {title}")
