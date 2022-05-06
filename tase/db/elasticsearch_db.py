from typing import Optional, List, Tuple

import pyrogram
from elasticsearch import Elasticsearch

from tase.db.elasticsearch_models import Audio


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
        if not Audio.has_index(self.es):
            Audio.create_index(self.es)

    def get_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional[Audio]:
        if message is None or message.audio is None:
            return None

        audio = Audio.get(self.es, Audio.get_id(message))
        if audio is None:
            # audio does not exist in the index, create it
            audio, successful = Audio.create(self.es, Audio.parse_from_message(message))
        return audio

    def update_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional[Audio]:
        if message is None or message.audio is None:
            return None

        audio = Audio.get(self.es, Audio.get_id(message))
        if audio is None:
            # audio does not exist in the index, create it
            audio, successful = Audio.create(self.es, Audio.parse_from_message(message))
        else:
            # audio exists in the index, update it
            audio, successful = Audio.update(self.es, audio, Audio.parse_from_message(message))

    def search_audio(
            self,
            query: str,
            from_: int = 0,
            size: int = 50
    ) -> Optional[Tuple[List[Audio], dict]]:
        if query is None or from_ is None or size is None:
            return None

        audios, search_metadata = Audio.search(self.es, query, from_, size)
        return audios, search_metadata

    def get_audio_by_download_url(self, download_url: str) -> Optional[Audio]:
        if download_url is None:
            return None
        return Audio.search_by_download_url(self.es, download_url)

    def get_audio_by_id(self, key: str) -> Optional[Audio]:
        if key is None:
            return None
        return Audio.search_by_id(self.es, key)