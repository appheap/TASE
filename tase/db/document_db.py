import uuid
from string import Template
from typing import Optional, Tuple

import pyrogram
from arango import ArangoClient
from arango.database import StandardDatabase

from tase.configs import ArangoDBConfig
from tase.db.document_models import Audio, BotTask, BotTaskStatus, BotTaskType, docs


class DocumentDatabase:
    arango_client: "ArangoClient"
    db: "StandardDatabase"

    def __init__(
        self,
        doc_db_config: ArangoDBConfig,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=doc_db_config.db_host_url)
        sys_db = self.arango_client.db(
            "_system",
            username=doc_db_config.db_username,
            password=doc_db_config.db_password,
        )

        if not sys_db.has_database(doc_db_config.db_name):
            sys_db.create_database(
                doc_db_config.db_name,
            )

        self.db = self.arango_client.db(
            doc_db_config.db_name,
            username=doc_db_config.db_username,
            password=doc_db_config.db_password,
        )

        self.aql = self.db.aql

        for doc in docs:
            if not self.db.has_collection(doc._doc_collection_name):
                _db = self.db.create_collection(doc._doc_collection_name)
            else:
                _db = self.db.collection(doc._doc_collection_name)
            doc._db = _db

    def create_audio(
        self, message: "pyrogram.types.Message", telegram_client_id: int
    ) -> Optional[Audio]:
        if message is None or message.audio is None or telegram_client_id is None:
            return None

        audio, successful = Audio.create(
            Audio.parse_from_message(message, telegram_client_id)
        )
        return audio

    def get_or_create_audio(
        self, message: "pyrogram.types.Message", telegram_client_id: int
    ) -> Optional[Audio]:
        if message is None or message.audio is None or telegram_client_id is None:
            return None

        audio = Audio.find_by_key(Audio.get_key(message, telegram_client_id))
        if not audio:
            # audio does not exist in the database, create it
            audio = self.create_audio(message, telegram_client_id)

        return audio

    def update_or_create_audio(
        self, message: "pyrogram.types.Message", telegram_client_id: int
    ) -> Optional[Audio]:
        if message is None or message.audio is None or telegram_client_id is None:
            return None

        audio = Audio.find_by_key(Audio.get_key(message, telegram_client_id))
        if audio:
            # audio exists in the database, update the audio
            audio, successful = Audio.update(
                audio, Audio.parse_from_message(message, telegram_client_id)
            )
        else:
            # audio does not exist in the database, create it
            audio = self.create_audio(message, telegram_client_id)

        return audio

    def get_audio_file_from_cache(self, audio, telegram_client_id) -> Optional[Audio]:
        if audio is None or telegram_client_id is None:
            return None
        return Audio.find_by_key(Audio.get_key_from_audio(audio, telegram_client_id))

    def create_bot_task(
        self,
        user_id: int,
        bot_id: int,
        task_type: "BotTaskType",
        state_dict: dict = None,
    ) -> Optional[Tuple[BotTask, bool]]:
        if user_id is None or bot_id is None or task_type is None:
            return None

        bot_task = BotTask(
            key=str(uuid.uuid4()),
            user_id=user_id,
            bot_id=bot_id,
            type=task_type,
        )
        if state_dict is not None and len(state_dict):
            bot_task.state_dict = state_dict

        task, successful = BotTask.create(bot_task)

        return task, successful

    def cancel_recent_bot_task(
        self,
        user_id: int,
        bot_id: int,
        task_type: "BotTaskType",
    ):
        if user_id is None or bot_id is None or task_type is None:
            return
        query_template = Template(
            "for doc_task in $doc_bot_tasks"
            "   sort doc_task.modified_at desc"
            "   filter doc_task.type==$type and doc_task.status==$status and doc_task.user_id==$user_id and "
            "doc_task.bot_id==$bot_id"
            "   return doc_task"
        )
        query = query_template.substitute(
            {
                "doc_bot_tasks": BotTask._doc_collection_name,
                "user_id": user_id,
                "bot_id": bot_id,
                "type": task_type.value,
                "status": BotTaskStatus.CREATED.value,
            }
        )

        cursor = self.aql.execute(
            query,
            count=True,
        )

        if cursor and len(cursor):
            for bot_task in cursor:
                bot_task = BotTask.parse_from_db(bot_task)
                bot_task._db.update(
                    {"_key": bot_task.key, "status": BotTaskStatus.CANCELED.value},
                    silent=True,
                )

    def update_task_state_dict(
        self,
        user_id: int,
        bot_id: int,
        task_type: "BotTaskType",
        new_task_state: dict,
    ):
        if (
            user_id is None
            or bot_id is None
            or task_type is None
            or new_task_state is None
        ):
            return

        query_template = Template(
            "for doc_task in $doc_bot_tasks"
            "   sort doc_task.modified_at desc"
            "   filter doc_task.type==$type and doc_task.status==$status and doc_task.user_id==$user_id and "
            "doc_task.bot_id==$bot_id"
            "   limit 1"
            "   return doc_task"
        )
        query = query_template.substitute(
            {
                "doc_bot_tasks": BotTask._doc_collection_name,
                "user_id": user_id,
                "bot_id": bot_id,
                "type": task_type.value,
                "status": BotTaskStatus.CREATED.value,
            }
        )

        cursor = self.aql.execute(
            query,
            count=True,
        )
        if cursor and len(cursor):
            bot_task = BotTask.parse_from_db(cursor.pop())
            if bot_task is not None:
                bot_task.state_dict.update(**new_task_state)
                bot_task._db.update(
                    {
                        "_key": bot_task.key,
                        "state_dict": bot_task.state_dict,
                    },
                    silent=True,
                )

    def get_latest_bot_task(self, user_id: int, bot_id: int) -> Optional[BotTask]:
        if user_id is None or bot_id is None:
            return

        query_template = Template(
            "for doc_task in $doc_bot_tasks"
            "   sort doc_task.modified_at desc"
            "   filter doc_task.status==$status and doc_task.user_id==$user_id and doc_task.bot_id==$bot_id"
            "   limit 1"
            "   return doc_task"
        )
        query = query_template.substitute(
            {
                "doc_bot_tasks": BotTask._doc_collection_name,
                "user_id": user_id,
                "bot_id": bot_id,
                "status": BotTaskStatus.CREATED.value,
            }
        )

        cursor = self.aql.execute(
            query,
            count=True,
        )
        if cursor and len(cursor):
            bot_task = BotTask.parse_from_db(cursor.pop())
            return bot_task
        else:
            return None
