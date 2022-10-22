import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin, logger

from tase.db import DatabaseClient
from .base_job import BaseJob
from ...common.utils import get_now_timestamp
from ...db.arangodb.enums import RabbitMQTaskType


class CountHitsJob(BaseJob):
    type = RabbitMQTaskType.COUNT_HITS_JOB
    priority = 2

    trigger = IntervalTrigger(
        minutes=10,
        start_date=arrow.now().datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        self.task_in_worker(db)

        job = db.document.get_count_hits_job()
        if job is None:
            self.task_failed(db)
        else:
            if job.is_active:
                now = get_now_timestamp()

                hits_count = db.graph.count_hits(
                    job.last_run_at,
                    now,
                )

                for hit_count in hits_count:
                    es_audio_doc = db.index.get_audio_by_id(hit_count.audio_key)
                    if not es_audio_doc:
                        continue

                    updated = es_audio_doc.update_by_hit_count(hit_count)
                    if not updated:
                        logger.error(f"Could not update hit count count for audio with key : `{hit_count.audio_key}`")

                updated = job.update_last_run(now)
                if not updated:
                    logger.error(f"Could not count hits job document")
                self.task_done(db)
            else:
                self.task_failed(db)
