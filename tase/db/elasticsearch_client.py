from typing import Tuple

from elasticsearch import Elasticsearch


class ElasticSearchClient:
    _es_client: 'Elasticsearch'

    def __init__(
            self,
            url: str,
            http_certs: str,
            basic_auth: Tuple[str, str]
    ):
        self._es_client = Elasticsearch(
            url,
            ca_certs=http_certs,
            basic_auth=basic_auth
        )


if __name__ == '__main__':
    es = ElasticSearchClient(
        'https://localhost:9200',
        http_certs='../../ca.crt',
        basic_auth=('elastic', 'abcdef')
    )
