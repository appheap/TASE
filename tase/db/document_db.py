from arango import ArangoClient
from arango.database import StandardDatabase

from tase.db.document_models import docs


class DocumentDatabase:
    arango_client: 'ArangoClient'
    db: 'StandardDatabase'

    def __init__(
            self,
            doc_db_config: dict,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=doc_db_config.get('db_host_url'))
        sys_db = self.arango_client.db(
            '_system',
            username=doc_db_config.get('db_username'),
            password=doc_db_config.get('db_password')
        )

        if not sys_db.has_database(doc_db_config.get('db_name')):
            sys_db.create_database(
                doc_db_config.get('db_name'),
            )

        self.db = self.arango_client.db(
            doc_db_config.get('db_name'),
            username=doc_db_config.get('db_username'),
            password=doc_db_config.get('db_password')
        )

        for doc in docs:
            if not self.db.has_collection(doc._doc_collection_name):
                setattr(self, doc._doc_collection_name, self.db.create_collection(doc._doc_collection_name))
            else:
                setattr(self, doc._doc_collection_name, self.db.collection(doc._doc_collection_name))
