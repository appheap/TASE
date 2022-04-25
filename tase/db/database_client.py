from typing import Optional

import pyrogram.types

from tase.db.graph_models.vertices import User, Chat, Audio
from tase.my_logger import logger
from .elasticsearch_db import ElasticsearchDatabase
from .graph_db import GraphDatabase


class DatabaseClient:
    _es_db: 'ElasticsearchDatabase'
    _graph_db: 'GraphDatabase'

    def __init__(
            self,
            elasticsearch_config: dict,
            graph_db_config: dict,
    ):

        self._es_db = ElasticsearchDatabase(
            elasticsearch_config=elasticsearch_config,
        )

        self._graph_db = GraphDatabase(
            graph_db_config=graph_db_config,
        )

    def create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None

        return self._graph_db.create_user(telegram_user)

    def create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None

        return self._graph_db.update_or_create_chat(telegram_chat, creator, member)

    def create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return

        try:
            self._es_db.get_or_create_audio(message)
            self._graph_db.update_or_create_audio(message)
        except Exception as e:
            logger.exception(e)


if __name__ == '__main__':
    es = DatabaseClient(
        'https://localhost:9200',
        elastic_http_certs='../../ca.crt',
        elastic_basic_auth=('elastic', 'abcdef')
    )

    offset = 0
    counter = 0
    while True:
        result = es._es_client.search(index='tase-test-index', size=1000, from_=offset)
        if len(result.body['hits']['hits']):
            offset += len(result.body['hits']['hits'])
            for obj_dict in result.body['hits']['hits']:
                # extract_audio(obj_dict)
                counter += 1
                if counter % 100 == 0:
                    logger.info(f'extracted {counter} audios')
                pass

        else:
            break
    print(result)
