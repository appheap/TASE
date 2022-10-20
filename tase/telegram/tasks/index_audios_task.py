import random
import time

from kombu.mixins import ConsumerProducerMixin
from pyrogram.errors import FloodWait

from tase.common.utils import datetime_to_timestamp, prettify
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import RabbitMQTaskType, TelegramAudioType
from tase.db.arangodb.graph.vertices import Chat
from tase.db.arangodb.helpers import AudioIndexerMetadata, AudioDocIndexerMetadata
from tase.db.db_utils import get_telegram_message_media_type
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient


class IndexAudiosTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.INDEX_AUDIOS_TASK

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
        except KeyError as e:
            logger.exception(e)
            self.task_failed(db)
        except FloodWait as e:
            self.task_failed(db)
            logger.exception(e)

            sleep_time = e.value + random.randint(1, 10)
            logger.info(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

        except Exception as e:
            logger.exception(e)
            self.task_failed(db)
        else:
            chat = db.graph.update_or_create_chat(tg_chat)

            if chat:
                self.index_audios(db, telegram_client, chat, index_audio=True)
                self.index_audios(db, telegram_client, chat, index_audio=False)

                logger.debug(f"Finished {title}")
                self.task_done(db)
            else:
                logger.debug(f"Error occurred: {title}")
                self.task_failed(db)
        finally:
            # wait for a while before starting to index a new channel
            time.sleep(random.randint(10, 20))

    def index_audios(
        self,
        db: DatabaseClient,
        telegram_client: TelegramClient,
        chat: graph_models.vertices.Chat,
        index_audio: bool = True,
    ):
        if index_audio:
            if chat.audio_indexer_metadata is not None:
                metadata: AudioIndexerMetadata = chat.audio_indexer_metadata.copy()
            else:
                metadata: AudioIndexerMetadata = AudioIndexerMetadata()
        else:
            if chat.audio_doc_indexer_metadata is not None:
                metadata: AudioDocIndexerMetadata = chat.audio_doc_indexer_metadata.copy()
            else:
                metadata: AudioDocIndexerMetadata = AudioDocIndexerMetadata()

        if metadata is None:
            self.task_failed(db)
            return

        metadata.reset_counters()

        for message in telegram_client.iter_messages(
            chat_id=chat.chat_id,
            offset_id=metadata.last_message_offset_id,
            only_newer_messages=True,
            filter="audio" if index_audio else "document",
        ):
            if not index_audio:
                audio, audio_type = get_telegram_message_media_type(message)
                if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                    continue

            successful = db.update_or_create_audio(
                message,
                telegram_client.telegram_id,
            )
            if successful:
                metadata.message_count += 1

            if message.id > metadata.last_message_offset_id:
                metadata.last_message_offset_id = message.id
                metadata.last_message_offset_date = datetime_to_timestamp(message.date)

        if index_audio:
            chat.update_audio_indexer_metadata(metadata)
        else:
            chat.update_audio_doc_indexer_metadata(metadata)

        logger.info(f"{prettify(metadata)}")
