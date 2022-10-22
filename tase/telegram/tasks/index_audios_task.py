import random
import time
from typing import Optional

from kombu.mixins import ConsumerProducerMixin
from pyrogram.errors import FloodWait

from tase.common.utils import datetime_to_timestamp, prettify, get_now_timestamp
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import RabbitMQTaskType, TelegramAudioType, ChatType
from tase.db.arangodb.graph.vertices import Chat
from tase.db.arangodb.helpers import AudioIndexerMetadata, AudioDocIndexerMetadata
from tase.db.db_utils import get_telegram_message_media_type
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.channel_analyzer import ChannelAnalyzer
from tase.telegram.client import TelegramClient


class IndexAudiosTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.INDEX_AUDIOS_TASK
    priority = 3

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

        if chat.audio_indexer_metadata is None or get_now_timestamp() - chat.audio_indexer_metadata.last_run_at > 24 * 60 * 60 * 1000:
            chat = self.get_updated_chat(telegram_client, db, chat)
            if chat:
                logger.info(f"Started indexing audio files from  `{chat.title}`")

                self.index_audios(db, telegram_client, chat, index_audio=True)
                self.index_audios(db, telegram_client, chat, index_audio=False)

                logger.info(f"Finished indexing audio files from `{chat.title}`")
                self.wait()
                self.task_done(db)
        else:
            logger.info(f"Cancelled indexing of {chat.title}")
            self.task_failed(db)

    @classmethod
    def wait(
        cls,
        sleep_time: int = random.randint(15, 25),
    ):
        # wait for a while before starting to index a new channel
        logger.info(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)
        logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

    def get_updated_chat(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
        chat: Chat,
    ) -> Optional[Chat]:
        extra_check = True if chat.audio_indexer_metadata is None else get_now_timestamp() - chat.audio_indexer_metadata.last_run_at > 8 * 60 * 60 * 1000
        successful = False
        new_chat = None

        if not telegram_client.peer_exists(chat.chat_id) or extra_check:
            # update the chat
            try:
                tg_chat = telegram_client.get_chat(chat.username if chat.username else chat.invite_link)
            except ValueError as e:
                # In case the chat invite link points to a chat that this telegram client hasn't joined yet.
                self.task_failed(db)
                logger.exception(e)
            except KeyError as e:
                self.task_failed(db)
                logger.exception(e)
            except FloodWait as e:
                self.task_failed(db)
                logger.exception(e)
                self.wait(e.value + random.randint(5, 15))
            except Exception as e:
                self.task_failed(db)
                logger.exception(e)
            else:
                new_chat = db.graph.update_or_create_chat(tg_chat)
                if not new_chat:
                    self.task_failed(db)
                else:
                    successful = True

            if successful:
                return new_chat
            else:
                return None
        else:
            return chat

    def index_audios(
        self,
        db: DatabaseClient,
        telegram_client: TelegramClient,
        chat: graph_models.vertices.Chat,
        index_audio: bool = True,
    ):
        calculate_score = False
        if index_audio:
            if chat.audio_indexer_metadata is not None:
                metadata: AudioIndexerMetadata = chat.audio_indexer_metadata.copy()
            else:
                metadata: AudioIndexerMetadata = AudioIndexerMetadata()
                calculate_score = True
        else:
            if chat.audio_doc_indexer_metadata is not None:
                metadata: AudioDocIndexerMetadata = chat.audio_doc_indexer_metadata.copy()
            else:
                metadata: AudioDocIndexerMetadata = AudioDocIndexerMetadata()

        if metadata is None:
            self.task_failed(db)
            return

        metadata.reset_counters()

        for idx, message in enumerate(
            telegram_client.iter_messages(
                chat_id=chat.chat_id,
                offset_id=metadata.last_message_offset_id,
                only_newer_messages=True,
                filter="audio" if index_audio else "document",
            )
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

            if idx % 200 == 0:
                self.wait(random.randint(5, 15))

        if index_audio:
            chat.update_audio_indexer_metadata(metadata)

            if calculate_score and chat.chat_type == ChatType.CHANNEL and chat.is_public:
                # sleep for a while
                self.wait(5)

                score = ChannelAnalyzer.calculate_score(
                    telegram_client,
                    chat.chat_id,
                    chat.members_count,
                )
                updated = chat.update_audio_indexer_score(score)
                logger.debug(f"Channel {chat.username} score: {score}")
        else:
            chat.update_audio_doc_indexer_metadata(metadata)

        logger.info(f"{prettify(metadata)}")
