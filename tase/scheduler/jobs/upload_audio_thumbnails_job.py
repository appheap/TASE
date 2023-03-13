import apscheduler.triggers.interval
import arrow
from kombu.mixins import ConsumerProducerMixin

import tase
from tase.telegram.tasks import UploadAudioThumbnailTask
from .base_job import BaseJob
from ...db.arangodb.enums import RabbitMQTaskType
from ...errors import NotEnoughRamError
from ...my_logger import logger
from ...telegram.client import TelegramClient


class UploadAudioThumbnailsJob(BaseJob):
    type = RabbitMQTaskType.UPLOAD_AUDIO_THUMBNAILS_JOB
    priority = 3

    trigger = apscheduler.triggers.interval.IntervalTrigger(
        hours=1,
        start_date=arrow.now().shift(seconds=+15).datetime,
    )

    async def run(
        self,
        consumer: ConsumerProducerMixin,
        db: tase.db.DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        await self.task_in_worker(db)

        failed = False

        unchecked_thumbnail_files = await db.document.get_unchecked_thumbnail_files()
        for thumbnail_file in unchecked_thumbnail_files:
            try:
                await UploadAudioThumbnailTask(
                    kwargs={
                        "downloaded_thumbnail_file_doc_key": thumbnail_file.key,
                    }
                ).publish(db)
            except NotEnoughRamError:
                logger.error(f"Uploading audio thumbnail task `{thumbnail_file.key}` was cancelled due to high memory usage")
                failed = True
                break
            except Exception as e:
                logger.exception(e)
                failed = True
                break

        if failed:
            await self.task_failed(db)
        else:
            await self.task_done(db)
