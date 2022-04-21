from elasticsearch import Elasticsearch


class ElasticsearchDatabase:
    es: 'Elasticsearch'

    def __init__(
            self,
            elasticsearch_config: 'dict',
    ):
        Elasticsearch(
            elasticsearch_config.get('cluster_url'),
            ca_certs=elasticsearch_config.get('https_certs_url'),
            basic_auth=(
                elasticsearch_config.get('basic_auth_username'),
                elasticsearch_config.get('basic_auth_password'))
        )
