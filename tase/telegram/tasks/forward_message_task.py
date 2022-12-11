import asyncio
import collections
import random
from typing import List, Tuple, Deque, Dict, Set

import pyrogram.types
from pyrogram.errors import FloodWait, MessageIdInvalid, ChatForwardsRestricted, UsernameNotOccupied, ChannelInvalid

from tase.configs import ClientTypes
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import RabbitMQTaskType, AudioType, TelegramAudioType
from tase.db.arangodb.graph.edges import ArchivedAudio
from tase.db.db_utils import get_telegram_message_media_type
from tase.db.elasticsearchdb import models as elasticsearch_models
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient
from tase.telegram.client.client_worker import RabbitMQConsumer


class ForwardMessageTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.FORWARD_MESSAGE_TASK
    priority = 5

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        await self.task_in_worker(db)

        if not telegram_client.archive_channel_info:
            await self.task_failed(db)
            return

        source_chat_id = self.kwargs.get("chat_id", None)
        source_message_ids = self.kwargs.get("message_ids", None)
        source_message_db_keys = self.kwargs.get("message_db_keys", None)

        try:
            if source_chat_id is None or not source_message_ids or not source_message_db_keys:
                await self.task_failed(db)
                return

            db_chat = await db.graph.get_chat_by_key(str(source_chat_id))
            if not db_chat or not db_chat.username:
                # todo: only forwarding from public channels is allowed for now.
                await self.task_failed(db)
                return

            db_audios = await db.graph.get_audios_from_keys(source_message_db_keys)
            if not db_audios:
                await self.task_failed(db)
                return

            es_audio_docs = await asyncio.gather(*(db.index.get_audio_by_id(db_audio.key) for db_audio in db_audios))
            if not es_audio_docs or len(es_audio_docs) != len(db_audios):
                await self.task_failed(db)
                return

            for es_audio_doc in es_audio_docs:
                if isinstance(es_audio_doc, BaseException):
                    await self.task_failed(db)
                    return

            db_audios_mapping = {db_audio.file_unique_id: (db_audio, es_audio_doc) for db_audio, es_audio_doc in zip(db_audios, es_audio_docs)}

            successful, db_chat = await self.get_updated_chat(db, db_chat, source_chat_id, telegram_client)
            if not successful or not db_chat:
                await self.task_failed(db)
                return

            successful, new_messages = await self.get_new_messages(
                db,
                source_chat_id,
                source_message_ids,
                telegram_client,
            )
            if not new_messages or not successful:
                await self.task_failed(db)
                return

            successful, forwardable_message_ids = await self.check_new_messages(
                telegram_client,
                db_audios,
                es_audio_docs,
                new_messages,
            )
            if not successful or not forwardable_message_ids:
                await self.task_failed(db)
                return

            # sleep for a while before forwarding messages
            await asyncio.sleep(random.randint(5, 15))

            # forward the forwardable messages
            successful, forwarded_messages = await self.forward_messages(
                telegram_client,
                forwardable_message_ids,
                source_chat_id,
            )
            if not successful or not forwarded_messages:
                await self.task_failed(db)
                return

            count = len(forwarded_messages)
            target_chat_id = telegram_client.archive_channel_info.chat_id

            logger.debug(
                f"[{telegram_client.name}] Forwarded {count} out of {len(forwardable_message_ids)} message(s) from `{db_chat.username}` to Archive Channel (`{telegram_client.archive_channel_info.chat_id}`) "
            )

            forwarded_file_unique_ids = await self.check_forwarded_messages(
                telegram_client,
                db,
                db_audios_mapping,
                forwarded_messages,
                target_chat_id,
            )

            await self.check_failed_forwarded_messages(
                telegram_client,
                db,
                forwardable_message_ids,
                forwarded_file_unique_ids,
                forwarded_messages,
                source_chat_id,
            )

        except FloodWait as e:
            await self.task_failed(db)
            logger.error(e)

            sleep_time = e.value + random.randint(5, 15)
            logger.info(f"Sleeping for {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)
            logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

        except Exception as e:
            # this is an unexpected error
            logger.exception(e)
            await self.task_failed(db)
        finally:
            await asyncio.sleep(random.randint(20, 30))

    async def check_failed_forwarded_messages(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
        forwardable_message_ids: Deque[int],
        forwarded_file_unique_ids: Set[str],
        forwarded_messages: List[pyrogram.types.Message],
        source_chat_id: int,
    ):
        if len(forwarded_messages) != len(forwardable_message_ids):
            not_forwarded_message_ids = [message.id for message in forwarded_messages if message.audio.file_unique_id not in forwarded_file_unique_ids]

            if not_forwarded_message_ids:
                logger.error(f"[{telegram_client.name}] Checking not forwarded messages for chat ID `{source_chat_id}` ...")

                not_forwarded_messages = await telegram_client.get_messages(chat_id=source_chat_id, message_ids=not_forwarded_message_ids)

                for message in not_forwarded_messages:
                    logger.error(f"message ID `{message}`=> empty: {message.empty}, media: {message.media}")
                    await db.update_or_create_audio(
                        message,
                        telegram_client.telegram_id,
                        source_chat_id,
                        AudioType.NOT_ARCHIVED,
                    )

    async def check_forwarded_messages(
        self,
        telegram_client: TelegramClient,
        db: DatabaseClient,
        db_audios_mapping: Dict[str, Tuple[graph_models.vertices.Audio, elasticsearch_models.Audio]],
        forwarded_messages: List[pyrogram.types.Message],
        target_chat_id: int,
    ) -> Set[str]:
        forwarded_file_unique_ids = set()

        for message in forwarded_messages:
            archived_audio_vertex = await db.graph.update_or_create_audio(
                message,
                target_chat_id,
                AudioType.ARCHIVED,
            )
            archived_audio_doc = await db.document.update_or_create_audio(
                message,
                telegram_client.telegram_id,
                target_chat_id,
            )

            if not archived_audio_vertex or not archived_audio_doc:
                logger.error(f"Error in creating audio doc or vertex for message ID `{message.id}` in chat `{target_chat_id}`")
                if archived_audio_vertex:
                    await archived_audio_vertex.delete()

                if archived_audio_doc:
                    await archived_audio_doc.delete()

                await message.delete()
                continue

            source_audio, es_source_audio_doc = db_audios_mapping.get(archived_audio_vertex.file_unique_id, (None, None))
            if source_audio and es_source_audio_doc and archived_audio_vertex:
                source_audio: graph_models.vertices.Audio = source_audio
                es_source_audio_doc: elasticsearch_models.Audio = es_source_audio_doc

                archived_audio_edge = await ArchivedAudio.get_or_create_edge(source_audio, archived_audio_vertex)
                if not archived_audio_edge:
                    logger.error(f"Error in creating archived audio edge from `{source_audio.key}` to `{archived_audio_vertex.key}`")
                    await message.delete()
                    await archived_audio_vertex.delete()
                    await archived_audio_doc.delete()
                else:
                    success = await source_audio.mark_as_archived(archived_audio_vertex.message_id)
                    es_success = await es_source_audio_doc.mark_as_archived(archived_audio_vertex.message_id)
                    if not success or not es_success:
                        logger.error(f"Error in marking `{source_audio.key}` as archived!")
                        await message.delete()
                        await archived_audio_vertex.delete()
                        await archived_audio_doc.delete()
                        await archived_audio_edge.delete()
                    else:
                        forwarded_file_unique_ids.add(archived_audio_vertex.file_unique_id)

        return forwarded_file_unique_ids

    async def forward_messages(
        self,
        telegram_client: TelegramClient,
        forwardable_message_ids: Deque[int],
        source_chat_id: int,
    ) -> Tuple[bool, List[pyrogram.types.Message]]:
        successful = False
        message_or_messages = []

        try:
            message_or_messages = await telegram_client.forward_messages(
                chat_id=telegram_client.archive_channel_info.chat_id,
                from_chat_id=source_chat_id,
                message_ids=list(forwardable_message_ids),
                drop_author=True,
                drop_media_captions=False,
            )
            if not isinstance(message_or_messages, list):
                message_or_messages = [message_or_messages]

            successful = True
        except MessageIdInvalid:
            logger.error(f"message ID is invalid")
        except ChatForwardsRestricted as e:
            logger.error(e)
        except UsernameNotOccupied as e:
            # todo: this username is no longer valid, mark audio from this chat as invalid
            logger.error(f"Chat `{source_chat_id}` is no longer valid!")
        except Exception as e:
            logger.exception(e)

        return successful, message_or_messages

    async def check_new_messages(
        self,
        telegram_client: TelegramClient,
        db_audios: Deque[graph_models.vertices.Audio],
        es_audio_docs: List[elasticsearch_models.Audio],
        new_messages: List[pyrogram.types.Message],
    ) -> Tuple[bool, Deque[int]]:
        forwardable_message_ids = collections.deque()
        successful = False

        for new_message, db_audio, es_audio_doc in zip(new_messages, db_audios, es_audio_docs):
            audio, telegram_audio_type = get_telegram_message_media_type(new_message)

            if audio is None or telegram_audio_type == TelegramAudioType.NON_AUDIO:
                # message is not valid anymore
                success = await db_audio.mark_as_non_audio()
                es_success = await es_audio_doc.mark_as_non_audio()
                if not success or not es_success:
                    logger.error(f"Error in marking `{db_audio.key}` as non-audio!")
            else:
                # message is valid, check if it is the same as the audio in the database
                if audio.file_unique_id == db_audio.file_unique_id:
                    # audio is the same as the audio in the database, forward it
                    if new_message.has_protected_content:
                        if telegram_client.client_type == ClientTypes.BOT:
                            forwardable_message_ids.append(new_message)
                        else:
                            # this message content is protected and cannot be forwarded by a user client.
                            logger.error(f"Message `{new_message.id}` from chat `{new_message.chat.id}` has content protection enabled!")
                    else:
                        forwardable_message_ids.append(new_message.id)
                else:
                    # message is not the same as the audio in the database, mark it as invalid
                    # todo: what if this audio is added to a playlist? should it be removed?
                    pass
                    # success = await db_audio.mark_as_non_audio()
                    # es_success = await es_audio_doc.mark_as_non_audio()
                    # if not success or not es_success:
                    #     logger.error(f"Error in marking `{db_audio.key}` as invalid!")
                    #     break
        else:
            successful = True

        return successful, forwardable_message_ids

    async def get_updated_chat(
        self,
        db: DatabaseClient,
        db_chat: graph_models.vertices.Chat,
        source_chat_id: int,
        telegram_client: TelegramClient,
    ) -> Tuple[bool, graph_models.vertices.Chat]:
        caught_exception = True

        if not await telegram_client.peer_exists(source_chat_id):
            try:
                tg_chat = await telegram_client.get_chat(db_chat.username)
                caught_exception = False
            except UsernameNotOccupied as e:
                # todo: this username is no longer valid, mark audio from this chat as invalid
                logger.error(f"Chat `{db_chat.username}` is no longer valid!")
            except Exception as e:
                logger.exception(e)
            else:
                db_chat = await db.graph.update_or_create_chat(tg_chat)
                await asyncio.sleep(30)
        else:
            caught_exception = False

        return not caught_exception, db_chat

    async def get_new_messages(
        self,
        db: DatabaseClient,
        source_chat_id: int,
        source_message_ids: List[int],
        telegram_client: TelegramClient,
    ) -> Tuple[bool, List[pyrogram.types.Message]]:
        new_messages = []
        successful = False

        try:
            new_messages = await telegram_client.get_messages(
                chat_id=source_chat_id,
                message_ids=source_message_ids,
            )
            successful = True
        except KeyError as e:
            # chat is no longer has that username or the username is invalid
            pass
        except ChannelInvalid as e:
            # The channel parameter is invalid
            pass
        except Exception as e:
            pass

        return successful, new_messages
