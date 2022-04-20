from dataclasses import field, dataclass

from .base_task import BaseTask
from .. import TelegramClient
from ...db.database_client import DatabaseClient


@dataclass
class IndexAudiosTask(BaseTask):
    name: str = field(default='index_audios_task')

    def run_task(self, telegram_client: 'TelegramClient', db: 'DatabaseClient'):
        chat_id = self.kwargs.get('chat_id', None)
        if chat_id is None:
            return

        last_offset_id = 0
        # retrieve the `last_offset_id` of the chat from database

        for message in telegram_client.iter_audios(chat_id=chat_id, offset_id=last_offset_id, only_newer_messages=True):
            if message.message_id > last_offset_id:
                last_offset_id = message.message_id

        # update the `last_offset_id` of the chat in the database
