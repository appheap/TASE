import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import logger

from tase.db import DatabaseClient
from .base_job import BaseJob
from ...common.utils import get_now_timestamp
from ...db.arangodb.enums import RabbitMQTaskType
from ...telegram.client.client_worker import RabbitMQConsumer


class CountHitsJob(BaseJob):
    type = RabbitMQTaskType.COUNT_HITS_JOB
    priority = 2

    trigger = IntervalTrigger(
        minutes=10,
        start_date=arrow.now().datetime,
    )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        await self.task_in_worker(db)

        job = await db.document.get_count_hits_job()
        if job is None:
            await self.task_failed(db)
        else:
            if job.is_active:
                now = get_now_timestamp()

                hits_count = await db.graph.count_hits(
                    job.last_run_at,
                    now,
                )

                for hit_count in hits_count:
                    es_audio_doc = await db.index.get_audio_by_id(hit_count.audio_key)
                    if not es_audio_doc:
                        continue

                    updated = await es_audio_doc.update_by_hit_count(hit_count)
                    if not updated:
                        logger.error(f"Could not update hit count count for audio with key : `{hit_count.audio_key}`")

                updated = await job.update_last_run(now)
                if not updated:
                    logger.error(f"Could not count hits job document")
                await self.task_done(db)
            else:
                await self.task_failed(db)
