import asyncio
import random
from typing import Optional

from pyrogram.errors import FloodWait

from tase.common.utils import get_now_timestamp, get_audio_thumbnail_vertices
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import RabbitMQTaskType, TelegramAudioType, AudioType
from tase.db.arangodb.graph.vertices import Chat
from tase.db.arangodb.helpers import AudioIndexerMetadata, AudioDocIndexerMetadata
from tase.db.db_utils import get_telegram_message_media_type
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient
from tase.telegram.client.client_worker import RabbitMQConsumer


class ReIndexAudiosTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.REINDEX_AUDIOS_TASK
    priority = 3

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        await self.task_in_worker(db)

        chat_key = self.kwargs.get("chat_key", None)

        chat: Chat = await db.graph.get_chat_by_key(chat_key)
        if chat is None:
            await self.task_failed(db)
            return

        if chat.audio_indexer_metadata is None or get_now_timestamp() - chat.audio_indexer_metadata.last_run_at > 1 * 24 * 60 * 60 * 1000:
            chat = await self.get_updated_chat(telegram_client, db, chat)
            if chat:
                logger.info(f"Started reindexing audio files from  `{chat.title}`")

                success = await self.index_audios(db, telegram_client, chat, index_audio=True)
                if success:
                    await self.wait()
                    await self.index_audios(db, telegram_client, chat, index_audio=False)

                logger.info(f"Finished reindexing audio files from `{chat.title}`")
                await self.wait()
                await self.task_done(db)
        else:
            logger.info(f"Cancelled reindexing of {chat.title}")
            await self.task_failed(db)

    @classmethod
    async def wait(
        cls,
        sleep_time: int = random.randint(15, 25),
    ):
        # wait for a while before starting to index a new channel
        logger.info(f"Sleeping for {sleep_time} seconds...")
        await asyncio.sleep(sleep_time)
        logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

    async def get_updated_chat(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
        chat: Chat,
    ) -> Optional[Chat]:
        extra_check = True if chat.audio_indexer_metadata is None else get_now_timestamp() - chat.audio_indexer_metadata.last_run_at > 14 * 24 * 60 * 60 * 1000
        successful = False
        new_chat = None

        if not await telegram_client.peer_exists(chat.chat_id) or extra_check:
            # update the chat
            try:
                tg_chat = await telegram_client.get_chat(chat.username if chat.username else chat.invite_link)
            except ValueError as e:
                # In case the chat invite link points to a chat that this telegram client hasn't joined yet.
                await self.task_failed(db)
                logger.exception(e)
            except KeyError as e:
                await self.task_failed(db)
                logger.exception(e)
            except FloodWait as e:
                await self.task_failed(db)
                logger.exception(e)
                await self.wait()
                # self.wait(e.value + random.randint(5, 15))
            except Exception as e:
                await self.task_failed(db)
                logger.exception(e)
            else:
                new_chat = await db.graph.update_or_create_chat(tg_chat)
                await self.wait()
                if not new_chat:
                    await self.task_failed(db)
                else:
                    successful = True

            if successful:
                return new_chat
            else:
                return None
        else:
            return chat

    async def index_audios(
        self,
        db: DatabaseClient,
        telegram_client: TelegramClient,
        chat: graph_models.vertices.Chat,
        index_audio: bool = True,
    ) -> bool:
        if index_audio:
            metadata: AudioIndexerMetadata = chat.audio_indexer_metadata
        else:
            metadata: AudioDocIndexerMetadata = chat.audio_doc_indexer_metadata

        try:
            idx = 0
            async for message in telegram_client.iter_messages(
                chat_id=chat.chat_id,
                offset_id=1,
                only_newer_messages=True,
                filter="audio" if index_audio else "document",
            ):
                if not index_audio:
                    audio, audio_type = get_telegram_message_media_type(message)
                    if audio is None or audio_type == TelegramAudioType.NON_AUDIO:
                        continue

                thumbs = await get_audio_thumbnail_vertices(db, telegram_client, message)
                successful = await db.update_or_create_audio(
                    message,
                    telegram_client.telegram_id,
                    chat.chat_id,
                    AudioType.NOT_ARCHIVED,
                    chat.get_chat_scores(),
                    thumbs,
                )

                if idx + 1 % 500 == 0:
                    await self.wait(random.randint(3, 10))

                idx += 1
                if idx >= metadata.last_message_offset_id:
                    # stop indexing after reaching the last indexed message
                    break

            if index_audio:
                await chat.update_audio_indexer_metadata(metadata)
            else:
                await chat.update_audio_doc_indexer_metadata(metadata)

        except Exception as e:
            await self.task_failed(db)
            logger.error("Got an exception")
            logger.exception(e)

            return False

        return True
