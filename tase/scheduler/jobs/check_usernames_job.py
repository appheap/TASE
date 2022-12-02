import asyncio
import random

import arrow
from apscheduler.triggers.interval import IntervalTrigger

import tase
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...errors import NotEnoughRamError
from ...my_logger import logger
from ...telegram.client import TelegramClient
from ...telegram.client.client_worker import RabbitMQConsumer
from ...telegram.tasks import CheckUsernameTask


class CheckUsernamesJob(BaseJob):
    type = RabbitMQTaskType.CHECK_USERNAMES_JOB
    priority = 1

    trigger = IntervalTrigger(
        hours=3,
        start_date=arrow.now().shift(hours=+1).datetime,
    )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        await self.task_in_worker(db)

        failed = False

        idx = 0
        async for username in db.graph.get_unchecked_usernames():
            # todo: blocking or non-blocking? which one is better suited for this case?
            try:
                await CheckUsernameTask(
                    kwargs={
                        "username_key": username.key,
                    }
                ).publish(db)
            except NotEnoughRamError:
                logger.debug(f"checking usernames for chat `{username.username}` was cancelled due to high memory usage")
                failed = True
                break
            else:
                if idx > 0 and idx % 10 == 0:
                    # fixme: sleep to avoid publishing many tasks while the others haven't been processed yet
                    await asyncio.sleep(10 * random.randint(10, 15))

                idx += 1

        if failed:
            await self.task_failed(db)
        else:
            await self.task_done(db)
