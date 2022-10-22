import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin

import tase
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...my_logger import logger
from ...telegram.client import TelegramClient


class CheckUsernamesWithUncheckedMentionsJob(BaseJob):
    type = RabbitMQTaskType.CHECK_USERNAMES_WITH_UNCHECKED_MENTIONS_JOB
    priority = 1

    trigger = IntervalTrigger(
        hours=3,
        minutes=30,
        start_date=arrow.now().shift(minutes=+10).datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        self.task_in_worker(db)
        for idx, (username, mentioned_chat) in enumerate(db.graph.get_checked_usernames_with_unchecked_mentions()):
            if username.is_checked:
                logger.info(f"Rechecking: {username.username}")
                if username.is_valid:
                    db.graph.create_and_check_mentions_edges_after_username_check(
                        mentioned_chat,
                        username,
                    )
                else:
                    # `mentioned_chat` is None
                    db.graph.update_mentions_edges_from_chat_to_username(username)

        self.task_done(db)
