from typing import List

import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import logger

from tase.db import DatabaseClient
from .base_job import BaseJob
from ...common.utils import get_now_timestamp
from ...db.arangodb.enums import RabbitMQTaskType
from ...db.arangodb.helpers import PlaylistInteractionCount
from ...telegram.client.client_worker import RabbitMQConsumer


class CountPublicPlaylistInteractionsJob(BaseJob):
    type = RabbitMQTaskType.COUNT_PUBLIC_PLAYLIST_INTERACTIONS_JOB
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

        job = await db.document.get_count_public_playlist_interactions_job()
        if job is None:
            await self.task_failed(db)
        else:
            if job.is_active:
                now = get_now_timestamp()

                interactions_count: List[PlaylistInteractionCount] = await db.graph.count_public_playlist_interactions(
                    job.last_run_at,
                    now,
                )

                for interaction_count in interactions_count:
                    es_playlist = await db.index.get_playlist_by_id(interaction_count.playlist_key)
                    if not es_playlist:
                        continue

                    updated = await es_playlist.update_by_interaction_count(interaction_count)
                    if not updated:
                        logger.error(f"Could not update interaction count for playlist with key : `{interaction_count.playlist_key}`")

                job_last_run_at = job.last_run_at
                updated = await job.update_last_run(now)
                if updated:
                    await db.graph.remove_invalid_public_playlist_interactions(job_last_run_at, now)
                else:
                    logger.error(f"Could not count interaction job document")

                await self.task_done(db)
            else:
                await self.task_failed(db)
