from dataclasses import field, dataclass

from .base_task import BaseTask, exception_handler
from .. import TelegramClient
from ...db.database_client import DatabaseClient
from ...my_logger import logger


@dataclass
class IndexAudiosTask(BaseTask):
    name: str = field(default='index_audios_task')

    @exception_handler
    def run_task(self, telegram_client: 'TelegramClient', db: 'DatabaseClient'):
        raise Exception('simple exception')
        chat_id = self.kwargs.get('chat_id', None)
        if chat_id is None:
            return

        last_offset_id = 1
        # retrieve the `last_offset_id` of the chat from database

        for message in telegram_client.iter_audios(chat_id=chat_id, offset_id=last_offset_id, only_newer_messages=True):
            db.create_audio(message)

            if message.message_id > last_offset_id:
                last_offset_id = message.message_id

        # update the `last_offset_id` of the chat in the database
        logger.info(last_offset_id)
