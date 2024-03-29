import asyncio
import random

from pyrogram.enums import ChatType
from pyrogram.errors import UsernameNotOccupied, FloodWait, ChannelInvalid

from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.channel_analyzer import ChannelAnalyzer
from tase.telegram.client import TelegramClient
from tase.telegram.client.client_worker import RabbitMQConsumer


class AddChannelTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.ADD_CHANNEL_TASK
    priority = 9

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        await self.task_in_worker(db)

        try:
            tg_chat = await telegram_client.get_chat(self.kwargs.get("channel_username"))

            # check if the chat is valid based on current policies of the bot
            if tg_chat.type == ChatType.CHANNEL:
                chat = await db.graph.update_or_create_chat(tg_chat)
                if chat is not None and chat.is_public:
                    score = await ChannelAnalyzer.calculate_score(
                        telegram_client,
                        chat.chat_id,
                        chat.members_count,
                    )
                    logger.debug(f"Channel {chat.username} score: {score}")
                    updated = chat.update_audio_indexer_score(score)

                    await self.task_done(db)
                else:
                    await self.task_done(db)
            else:
                await self.task_failed(db)
        except UsernameNotOccupied:
            # The username is not occupied by anyone
            await self.task_failed(db)
        except ValueError as e:
            # In case the chat invite link points to a chat this telegram client hasn't joined yet.
            # todo: send an appropriate message to notify the user of this situation
            await self.task_failed(db)
        except KeyError as e:
            # the provided username is not valid
            # todo: send an appropriate message to notify the user of this situation
            await self.task_failed(db)
        except ChannelInvalid as e:
            # the channel is invalid
            # todo: send an appropriate message to notify the user of this situation
            await self.task_failed(db)
        except FloodWait as e:
            await self.task_failed(db)
            logger.exception(e)

            sleep_time = e.value + random.randint(5, 15)
            logger.info(f"Sleeping for {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)
            logger.info(f"Waking up after sleeping for {sleep_time} seconds...")

        except Exception as e:
            # this is an unexpected error
            logger.exception(e)
            await self.task_failed(db)
        finally:
            # sleep for a while before adding another channel
            await asyncio.sleep(random.randint(15, 25))
