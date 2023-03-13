import asyncio
import random

from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient
from tase.telegram.client.client_worker import RabbitMQConsumer


class UploadAudioThumbnailTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.UPLOAD_AUDIO_THUMBNAIL_TASK
    priority = 3

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        await self.task_in_worker(db)

        thumbnail_file_doc_key = self.kwargs.get("thumbnail_file_doc_key", None)

        thumbnail_file_doc = await db.document.get_thumbnail_file_by_key(thumbnail_file_doc_key)
        if not thumbnail_file_doc:
            await self.task_failed(db)
            return

        downloaded_thumb_file_path = f"downloads/{thumbnail_file_doc.file_name}.jpg"

        try:
            uploaded_photo_message = await telegram_client._client.send_photo(
                telegram_client.thumbnail_archive_channel_info.chat_id,
                downloaded_thumb_file_path,
                caption=f"thumb_file_unique_id: {thumbnail_file_doc.thumbnail_file_unique_id}",
            )
        except Exception as e:
            await self.task_failed(db)
            logger.exception(e)
        else:
            wait_time = random.randint(3, 7) + random.randint(1, 3)
            logger.debug(f"Sleeping for {wait_time} seconds after uploading thumbnail photo...")
            await asyncio.sleep(wait_time)

            if uploaded_photo_message:
                await thumbnail_file_doc.mark_as_checked()

                await db.update_audio_thumbnails(
                    telegram_client.telegram_id,
                    thumbnail_file_doc.thumbnail_file_unique_id,
                    uploaded_photo_message,
                    thumbnail_file_doc.file_hash,
                )

                await self.task_done(db)
            else:
                await self.task_failed(db)
