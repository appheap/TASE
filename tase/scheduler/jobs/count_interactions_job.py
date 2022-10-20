import arrow
from apscheduler.triggers.interval import IntervalTrigger
from kombu.mixins import ConsumerProducerMixin, logger

from tase.db import DatabaseClient
from .base_job import BaseJob
from ...common.utils import get_now_timestamp
from ...db.arangodb.enums import RabbitMQTaskType


class CountInteractionsJob(BaseJob):
    type = RabbitMQTaskType.COUNT_INTERACTIONS_JOB

    trigger = IntervalTrigger(
        hours=1,
        start_date=arrow.now().datetime,
    )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        self.task_in_worker(db)

        job = db.document.get_count_interactions_job()
        if job is None:
            self.task_failed(db)
        else:
            if job.is_active:
                now = get_now_timestamp()

                interactions_count = db.graph.count_interactions(
                    job.last_run_at,
                    now,
                )

                for interaction_count in interactions_count:
                    es_audio_doc = db.index.get_audio_by_id(interaction_count.audio_key)
                    if not es_audio_doc:
                        continue

                    updated = es_audio_doc.update_by_interaction_count(interaction_count)
                    if not updated:
                        logger.error(f"Could not update interaction count for audio with key : `{interaction_count.audio_key}`")

                updated = job.update_last_run(now)
                if not updated:
                    logger.error(f"Could not count interaction job document")
                self.task_done(db)
            else:
                self.task_failed(db)
