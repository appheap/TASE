from typing import Optional

import pyrogram
from elasticsearch import Elasticsearch, NotFoundError

from tase.db.elasticsearch_models.audio import Audio
from tase.my_logger import logger


class ElasticsearchDatabase:
    es: 'Elasticsearch'

    def __init__(
            self,
            elasticsearch_config: 'dict',
    ):
        self.es = Elasticsearch(
            elasticsearch_config.get('cluster_url'),
            ca_certs=elasticsearch_config.get('https_certs_url'),
            basic_auth=(
                elasticsearch_config.get('basic_auth_username'),
                elasticsearch_config.get('basic_auth_password'))
        )

    def get_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return None

        audio = None
        try:
            response = self.es.get(index=Audio._index_name, id=Audio.get_id(message))
            audio = Audio.parse_from_db(response)
        except NotFoundError as e:
            # audio does not exist in the index, create it
            audio = Audio.parse_from_message(message)
            id, doc = audio.parse_for_db()
            if id and doc:
                response = self.es.create(
                    index=Audio._index_name,
                    id=id,
                    document=doc
                )
                logger.info(response)
            # logger.exception(e)
        except Exception as e:
            logger.exception(e)

        return audio
