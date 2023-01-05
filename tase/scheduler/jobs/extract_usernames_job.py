from typing import AsyncGenerator

import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.my_logger import logger
from tase.telegram.tasks import ExtractUsernamesTask
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...db.arangodb.graph.vertices import Chat
from ...errors import NotEnoughRamError
from ...telegram.client import TelegramClient


class ExtractUsernamesJob(BaseJob):
    type = RabbitMQTaskType.EXTRACT_USERNAMES_JOB
    priority = 1

    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=4,
        start_date=arrow.now().shift(minutes=+30).datetime,
    )

    async def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        await self.task_in_worker(db)

        db_chats = db.graph.get_chats_sorted_by_username_extractor_score()
        not_extracted_db_chats = db.graph.get_chats_sorted_by_username_extractor_score(only_include_indexed_chats=False)

        if await self.extract(db, db_chats):
            failed_ = await self.extract(db, not_extracted_db_chats)
            if failed_:
                await self.task_failed(db)
            else:
                await self.task_done(db)
        else:
            await self.task_failed(db)

    @staticmethod
    async def extract(
        db: tase.db.DatabaseClient,
        chats: AsyncGenerator[Chat, None],
    ) -> bool:
        if not chats:
            return False

        failed = False

        async for chat in chats:
            logger.debug(chat.username)
            # todo: blocking or non-blocking? which one is better suited for this case?
            try:
                await ExtractUsernamesTask(
                    kwargs={
                        "chat_key": chat.key,
                    }
                ).publish(db)
            except NotEnoughRamError:
                logger.debug(f"Extracting usernames from chat `{chat.username}` was cancelled due to high memory usage")
                failed = True
                break

        return failed
