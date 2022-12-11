import asyncio
import collections

import arrow
from apscheduler.triggers.interval import IntervalTrigger
from decouple import config

from tase.db import DatabaseClient
from tase.my_logger import logger
from .base_job import BaseJob
from ...common.utils import group_list_by_step
from ...db.arangodb.enums import RabbitMQTaskType
from ...task_distribution import TargetWorkerType
from ...telegram.client.client_worker import RabbitMQConsumer
from ...telegram.tasks import ForwardMessageTask


class ForwardAudiosJob(BaseJob):
    type = RabbitMQTaskType.FORWARD_AUDIOS_JOB
    priority = 1

    trigger = IntervalTrigger(
        hours=6,
        start_date=arrow.now().shift(seconds=+30).datetime,
    )

    async def run(
        self,
        consumer: RabbitMQConsumer,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        await self.task_in_worker(db)
        logger.info("Started forwarding audios job...")

        audio_groups = await db.graph.get_not_archived_downloaded_audios()
        if audio_groups:
            not_protected_content_message_ids = collections.deque()
            not_protected_content_message_db_keys = collections.deque()

            protected_content_message_ids = collections.deque()
            protected_content_message_db_keys = collections.deque()
            for idx, audio_group in enumerate(audio_groups):
                current_chat_id = None
                for audio in audio_group:
                    if not current_chat_id:
                        current_chat_id = audio.chat_id

                    if audio.has_protected_content:
                        protected_content_message_ids.append(audio.message_id)
                        protected_content_message_db_keys.append(audio.key)
                    else:
                        not_protected_content_message_ids.append(audio.message_id)
                        not_protected_content_message_db_keys.append(audio.key)

                if not_protected_content_message_ids:
                    for messages_ids, message_db_keys in zip(
                        group_list_by_step(list(not_protected_content_message_ids)),
                        group_list_by_step(list(not_protected_content_message_db_keys)),
                    ):
                        status, created = await ForwardMessageTask(
                            kwargs={
                                "chat_id": current_chat_id,
                                "message_ids": messages_ids,
                                "message_db_keys": message_db_keys,
                            },
                        ).publish(db)
                if protected_content_message_ids:
                    running_bot_name = config("RUNNING_BOT_NAME")
                    if running_bot_name:
                        for messages_ids, message_db_keys in zip(
                            group_list_by_step(list(protected_content_message_ids)),
                            group_list_by_step(list(protected_content_message_db_keys)),
                        ):
                            status, created = await ForwardMessageTask(
                                kwargs={
                                    "chat_id": current_chat_id,
                                    "message_ids": messages_ids,
                                    "message_db_keys": message_db_keys,
                                },
                                target_worker_type=TargetWorkerType.ONE_TELEGRAM_BOT_CONSUMER_WORK,
                            ).publish(
                                db,
                                target_queue_routing_key=running_bot_name,
                            )

                del current_chat_id
                not_protected_content_message_ids.clear()
                not_protected_content_message_db_keys.clear()
                protected_content_message_ids.clear()
                protected_content_message_db_keys.clear()

                if (idx + 1) % 2 == 0:
                    await asyncio.sleep(20)

        await self.task_done(db)
