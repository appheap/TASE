from typing import AsyncGenerator

import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.telegram.tasks import IndexAudiosTask
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...db.arangodb.graph.vertices import Chat
from ...errors import NotEnoughRamError
from ...my_logger import logger
from ...telegram.client import TelegramClient


class IndexAudiosJob(BaseJob):
    type = RabbitMQTaskType.INDEX_AUDIOS_JOB
    priority = 3

    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(minutes=+1).datetime,
    )

    async def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        await self.task_in_worker(db)

        chats = db.graph.get_chats_sorted_by_audio_indexer_score(only_include_indexed_chats=True)
        not_indexed_chats = db.graph.get_chats_sorted_by_audio_indexer_score(only_include_indexed_chats=False)

        if await self.index_audios(db, chats):
            failed = await self.index_audios(db, not_indexed_chats)
            if failed:
                await self.task_failed(db)
            else:
                await self.task_done(db)
        else:
            await self.task_failed(db)

    @staticmethod
    async def index_audios(
        db: tase.db.DatabaseClient,
        chats: AsyncGenerator[Chat, None],
    ) -> bool:
        failed = False

        # todo: blocking or non-blocking? which one is better suited for this case?
        async for chat in chats:
            logger.info(f"published task for indexing: {chat.username}")
            try:
                await IndexAudiosTask(
                    kwargs={
                        "chat_key": chat.key,
                    }
                ).publish(db)
            except NotEnoughRamError:
                logger.error(f"indexing audio files from chat `{chat.username}` was cancelled due to high memory usage")
                failed = True
                break
            except Exception as e:
                logger.exception(e)
                failed = True
                break

        return failed
