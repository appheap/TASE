import arrow
from apscheduler.triggers.interval import IntervalTrigger

import tase
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...my_logger import logger
from ...telegram.client import TelegramClient
from ...telegram.client.client_worker import RabbitMQConsumer


class CheckUsernamesWithUncheckedMentionsJob(BaseJob):
    type = RabbitMQTaskType.CHECK_USERNAMES_WITH_UNCHECKED_MENTIONS_JOB
    priority = 1

    trigger = IntervalTrigger(
        hours=3,
        minutes=30,
        start_date=arrow.now().shift(minutes=+10).datetime,
    )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        await self.task_in_worker(db)
        idx = 0
        async for username, mentioned_chat in db.graph.get_checked_usernames_with_unchecked_mentions():
            idx += 1
            if username.is_checked:
                logger.info(f"Rechecking: {username.username}")
                if username.is_valid:
                    await db.graph.create_and_check_mentions_edges_after_username_check(
                        mentioned_chat,
                        username,
                    )
                else:
                    # `mentioned_chat` is None
                    await db.graph.update_mentions_edges_from_chat_to_username(username)

        await self.task_done(db)
