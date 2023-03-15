import asyncio
import os
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

        downloaded_thumbnail_file_doc = self.kwargs.get("downloaded_thumbnail_file_doc_key", None)

        downloaded_thumbnail_file_doc = await db.document.get_downloaded_thumbnail_file_by_key(downloaded_thumbnail_file_doc)
        if not downloaded_thumbnail_file_doc:
            await self.task_failed(db)
            return

        downloaded_thumb_file_path = f"downloads/{downloaded_thumbnail_file_doc.file_name}.jpg"
        if not os.path.exists(downloaded_thumb_file_path) or not os.path.isfile(downloaded_thumb_file_path):
            await self.task_failed(db)
            logger.error(f"Path for the thumbnail file does not exist!: `{downloaded_thumb_file_path}`")
            return

        # Don't upload the file if it is already uploaded!
        if await db.graph.get_thumbnail_file_by_file_hash(downloaded_thumbnail_file_doc.file_hash):
            await self.task_failed(db)
            logger.debug(f"This thumbnail file is already uploaded!: `{downloaded_thumbnail_file_doc.file_hash}")
            return

        # check whether the file has downloaded correctly by checking its size
        if not os.path.getsize(downloaded_thumb_file_path):
            await self.task_failed(db)
            logger.debug(f"This thumbnail file size is zero!: `{downloaded_thumbnail_file_doc.file_name}")
            return

        try:
            uploaded_photo_message = await telegram_client._client.send_photo(
                telegram_client.thumbnail_archive_channel_info.chat_id,
                downloaded_thumb_file_path,
                caption=downloaded_thumbnail_file_doc.file_hash,
            )
        except Exception as e:
            await self.task_failed(db)
            logger.exception(e)
        else:
            if uploaded_photo_message:
                await downloaded_thumbnail_file_doc.mark_as_checked()

                await db.update_audio_thumbnails(
                    telegram_client.telegram_id,
                    downloaded_thumbnail_file_doc.thumbnail_file_unique_id,
                    uploaded_photo_message,
                    downloaded_thumbnail_file_doc.file_hash,
                )

                # remove the downloaded thumbnail file to free space
                os.remove(downloaded_thumb_file_path)

                await self.task_done(db)
            else:
                await self.task_failed(db)

            wait_time = random.randint(4, 10)
            logger.debug(f"Sleeping for {wait_time} seconds after uploading thumbnail photo...")
            await asyncio.sleep(wait_time)
