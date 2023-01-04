import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import logger

from tase.db import DatabaseClient
from .base_job import BaseJob
from ...common.utils import get_now_timestamp
from ...db.arangodb.enums import RabbitMQTaskType
from ...telegram.client.client_worker import RabbitMQConsumer


class CountAudioInteractionsJob(BaseJob):
    type = RabbitMQTaskType.COUNT_AUDIO_INTERACTIONS_JOB
    priority = 2

    trigger = IntervalTrigger(
        hours=1,
        start_date=arrow.now().datetime,
    )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        await self.task_in_worker(db)

        job = await db.document.get_count_audio_interactions_job()
        if job is None:
            await self.task_failed(db)
        else:
            if job.is_active:
                now = get_now_timestamp()

                interactions_count = await db.graph.count_audio_interactions(
                    job.last_run_at,
                    now,
                )

                for interaction_count in interactions_count:
                    es_audio_doc = await db.index.get_audio_by_id(interaction_count.vertex_key)
                    if not es_audio_doc:
                        continue

                    updated = await es_audio_doc.update_by_interaction_count(interaction_count)
                    if not updated:
                        logger.error(f"Could not update interaction count for audio with key : `{interaction_count.vertex_key}`")

                updated = job.update_last_run(now)
                if not updated:
                    logger.error(f"Could not count interaction job document")
                await self.task_done(db)
            else:
                await self.task_failed(db)
