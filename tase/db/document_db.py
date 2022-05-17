from typing import Optional

import pyrogram
from arango import ArangoClient
from arango.collection import StandardCollection
from arango.database import StandardDatabase

from tase.configs import ArangoDBConfig
from tase.db.document_models import Audio, docs


class DocumentDatabase:
    arango_client: 'ArangoClient'
    db: 'StandardDatabase'

    doc_audios: 'StandardCollection'

    def __init__(
            self,
            doc_db_config: ArangoDBConfig,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=doc_db_config.db_host_url)
        sys_db = self.arango_client.db(
            '_system',
            username=doc_db_config.db_username,
            password=doc_db_config.db_password
        )

        if not sys_db.has_database(doc_db_config.db_name):
            sys_db.create_database(
                doc_db_config.db_name,
            )

        self.db = self.arango_client.db(
            doc_db_config.db_name,
            username=doc_db_config.db_username,
            password=doc_db_config.db_password
        )

        for doc in docs:
            if not self.db.has_collection(doc._doc_collection_name):
                setattr(self, doc._doc_collection_name, self.db.create_collection(doc._doc_collection_name))
            else:
                setattr(self, doc._doc_collection_name, self.db.collection(doc._doc_collection_name))

    def create_audio(
            self,
            message: 'pyrogram.types.Message',
            telegram_client_id: int
    ) -> Optional[Audio]:
        if message is None or message.audio is None or telegram_client_id is None:
            return None

        audio, successful = Audio.create(self.doc_audios, Audio.parse_from_message(message, telegram_client_id))
        return audio

    def get_or_create_audio(
            self,
            message: 'pyrogram.types.Message',
            telegram_client_id: int
    ) -> Optional[Audio]:
        if message is None or message.audio is None or telegram_client_id is None:
            return None

        audio = Audio.find_by_key(self.doc_audios, Audio.get_key(message, telegram_client_id))
        if not audio:
            # audio does not exist in the database, create it
            audio = self.create_audio(message, telegram_client_id)

        return audio

    def update_or_create_audio(
            self,
            message: 'pyrogram.types.Message',
            telegram_client_id: int
    ) -> Optional[Audio]:
        if message is None or message.audio is None or telegram_client_id is None:
            return None

        audio = Audio.find_by_key(self.doc_audios, Audio.get_key(message, telegram_client_id))
        if audio:
            # audio exists in the database, update the audio
            audio, successful = Audio.update(self.doc_audios, audio,
                                             Audio.parse_from_message(message, telegram_client_id))
        else:
            # audio does not exist in the database, create it
            audio = self.create_audio(message, telegram_client_id)

        return audio

    def get_audio_file_from_cache(self, audio, telegram_client_id) -> Optional[Audio]:
        if audio is None or telegram_client_id is None:
            return None
        return Audio.find_by_key(self.doc_audios, Audio.get_key_from_audio(audio, telegram_client_id))
