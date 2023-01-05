from typing import List

import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import logger

from tase.db import DatabaseClient
from .base_job import BaseJob
from ...common.utils import get_now_timestamp
from ...db.arangodb.enums import RabbitMQTaskType
from ...db.arangodb.helpers import PublicPlaylistSubscriptionCount
from ...telegram.client.client_worker import RabbitMQConsumer


class CountPublicPlaylistSubscriptionsJob(BaseJob):
    type = RabbitMQTaskType.COUNT_PUBLIC_PLAYLIST_SUBSCRIPTIONS_JOB
    priority = 2

    trigger = IntervalTrigger(
        minutes=1,
        start_date=arrow.now().datetime,
    )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        await self.task_in_worker(db)

        job = await db.document.get_count_public_playlist_subscriptions_job()
        if job is None:
            await self.task_failed(db)
        else:
            if job.is_active:
                now = get_now_timestamp()

                subscriptions_count: List[PublicPlaylistSubscriptionCount] = await db.graph.count_public_playlist_subscriptions(
                    job.last_run_at,
                    now,
                )

                for subscription_count in subscriptions_count:
                    es_playlist = await db.index.get_playlist_by_id(subscription_count.playlist_key)
                    if not es_playlist:
                        continue

                    updated = await es_playlist.update_by_subscription_count(subscription_count)
                    if not updated:
                        logger.error(f"Could not update public playlist subscription count for playlist with key : `{subscription_count.playlist_key}`")

                updated = await job.update_last_run(now)
                if not updated:
                    logger.error(f"Could not count public playlist subscription job document")
                await self.task_done(db)
            else:
                await self.task_failed(db)
