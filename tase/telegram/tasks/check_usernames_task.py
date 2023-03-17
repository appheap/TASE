import asyncio
import random

from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, FloodWait, ChannelInvalid

from tase.common.utils import get_now_timestamp
from tase.db import DatabaseClient
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import RabbitMQTaskType, ChatType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.channel_analyzer import ChannelAnalyzer
from tase.telegram.client import TelegramClient
from tase.telegram.client.client_worker import RabbitMQConsumer


class CheckUsernameTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.CHECK_USERNAME_TASK
    priority = 1

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        await self.task_in_worker(db)

        username_key = self.kwargs.get("username_key", None)
        username_vertex: graph_models.vertices.Username = await db.graph.get_username_by_key(username_key)
        if username_vertex is None or username_vertex.username is None or username_vertex.is_checked:
            await self.task_failed(db)
            return

        logger.info(f"Checking: {username_vertex.username}")
        try:
            tg_mentioned_chat = await telegram_client.get_chat(username_vertex.username)
        except (KeyError, ValueError, UsernameNotOccupied, UsernameInvalid, ChannelInvalid) as e:
            # ValueError: In case the chat invite link points to a chat that this telegram client hasn't joined yet.
            # KeyError or UsernameNotOccupied: The username is not occupied by anyone, so update the username.
            # UsernameInvalid: The username is invalid.
            # ChannelInvalid: The channel is invalid.
            logger.info(f"Username `{username_vertex.username}` is invalid")

            if await username_vertex.check(True, get_now_timestamp(), False):
                await db.graph.update_mentions_edges_from_chat_to_username(username_vertex)
            else:
                # todo: update wasn't successful, what now?
                raise Exception("Unexpected error")

            await self.task_done(db)

        except FloodWait as e:
            # fixme: find a solution for this
            await self.task_failed(db)

            # sleep_time = e.value + random.randint(5, 15)
            # logger.info(f"Sleeping for {sleep_time} seconds...")
            # await asyncio.sleep(sleep_time)
            # logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

        except Exception as e:
            logger.exception(e)
            await self.task_failed(db)
        else:
            logger.info(f"Username `{username_vertex.username}` is valid")

            mentioned_chat = await db.graph.update_or_create_chat(tg_mentioned_chat)

            if mentioned_chat:
                # the username is valid, update the username and create new edge from the original chat to the
                # mentioned chat
                if await username_vertex.check(True, get_now_timestamp(), True):
                    # update `mentions` edges and `Username` vertices, Also, create new edges from `Username`
                    # vertices to `Chat` vertices and create edges from `Chat` to `Chat` vertices
                    await db.graph.create_and_check_mentions_edges_after_username_check(
                        mentioned_chat,
                        username_vertex,
                    )

                    if mentioned_chat.chat_type == ChatType.CHANNEL and mentioned_chat.is_public:
                        # wait for a while
                        await asyncio.sleep(5)

                        score = await ChannelAnalyzer.calculate_score(
                            telegram_client,
                            mentioned_chat.chat_id,
                            mentioned_chat.members_count,
                        )
                        updated = await mentioned_chat.update_audio_indexer_score(score)
                        logger.debug(f"Channel {mentioned_chat.username} score: {score}")

                    await self.task_done(db)
                else:
                    # todo: update wasn't successful, what now?
                    await self.task_failed(db)
                    raise Exception("Unexpected error")
            else:
                # fixme: this must not happen
                await self.task_failed(db)
                raise Exception("Unexpected error")

        finally:
            # this is necessary to avoid flood errors
            # todo: is this one good enough?
            await asyncio.sleep(random.randint(20, 30))
