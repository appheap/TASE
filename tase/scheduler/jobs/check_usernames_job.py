import random
import time

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
        self.task_in_worker(db)
        usernames = db.graph.get_unchecked_usernames()

        failed = False

        for idx, username in enumerate(usernames):
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
                    time.sleep(10 * random.randint(10, 15))

        if failed:
            self.task_failed(db)
        else:
            self.task_done(db)
