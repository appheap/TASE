from typing import Optional

from kombu.mixins import ConsumerProducerMixin

from tase.common.utils import datetime_to_timestamp, prettify
from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.db.arangodb.graph.vertices import Chat
from tase.db.arangodb.helpers import AudioIndexerMetadata
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient


class IndexAudiosTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.INDEX_AUDIOS_TASK

    metadata: Optional[AudioIndexerMetadata]

    def run(
        self,
        consumer_producer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        self.task_in_worker(db)

        chat_key = self.kwargs.get("chat_key", None)

        chat: Chat = db.graph.get_chat_by_key(chat_key)
        if chat is None:
            self.task_failed(db)
            return

        chat_id = chat.username if chat.username else chat.invite_link
        title = chat.title

        try:
            tg_chat = telegram_client.get_chat(chat_id)
        except ValueError as e:
            # In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # todo: fix this
            logger.exception(e)
            self.task_failed(db)
        except Exception as e:
            logger.exception(e)
            self.task_failed(db)
        else:
            chat = db.graph.update_or_create_chat(tg_chat)

            if chat:
                self.metadata = chat.audio_indexer_metadata.copy()
                if self.metadata is None:
                    self.task_failed(db)
                    return
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

                self.task_done(db)
            else:
                logger.debug(f"Error occurred: {title}")
                self.task_failed(db)
