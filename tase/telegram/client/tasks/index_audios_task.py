from typing import Optional

from pydantic import Field

from tase.db import DatabaseClient
from tase.db.arangodb.graph.vertices import Chat
from tase.db.arangodb.helpers import AudioIndexerMetadata
from tase.my_logger import logger
from tase.telegram.client import TelegramClient
from tase.utils import datetime_to_timestamp, prettify
from .base_task import BaseTask


class IndexAudiosTask(BaseTask):
    name: str = Field(default="index_audios_task")

    metadata: Optional[AudioIndexerMetadata]

    def run_task(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
    ):
        chat: Chat = self.kwargs.get("chat")
        if chat is None:
            return

        chat_id = chat.username if chat.username else chat.invite_link
        title = chat.title

        try:
            tg_chat = telegram_client.get_chat(chat_id)
        except ValueError as e:
            # In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # todo: fix this
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        else:
            chat = db.graph.update_or_create_chat(tg_chat)

            if chat:
                self.metadata = chat.audio_indexer_metadata
                self.metadata.reset_counters()

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
                        self.metadata.last_message_offset_date = datetime_to_timestamp(
                            message.date
                        )

                chat.update_audio_indexer_metadata(self.metadata)
                logger.info(f"{prettify(self.metadata)}")
                logger.debug(f"Finished {title}")
            else:
                logger.debug(f"Error occurred: {title}")
