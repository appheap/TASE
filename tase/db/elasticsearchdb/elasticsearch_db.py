from elasticsearch import logger, AsyncElasticsearch

from tase.configs import ElasticConfig
from tase.db.elasticsearchdb.models import elasticsearch_indices


class ElasticsearchDatabase:
    es: AsyncElasticsearch

    def __init__(
        self,
        elasticsearch_config: ElasticConfig,
    ):
        self.es = AsyncElasticsearch(
            elasticsearch_config.cluster_url,
            ca_certs=elasticsearch_config.https_certs_url,
            basic_auth=(
                elasticsearch_config.basic_auth_username,
                elasticsearch_config.basic_auth_password,
            ),
            timeout=120,
        )

    async def init_database(self):
        for index_cls in elasticsearch_indices:
            index_cls._es = self.es

            if not await index_cls.has_index():
                try:
                    created = await index_cls.create_index()
                except Exception as e:
                    logger.exception(f"Could not create the {index_cls._index_name} Index")
                else:
                    if not created:
                        logger.error(f"Could not create the {index_cls._index_name} Index")
