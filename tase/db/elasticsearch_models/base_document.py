from typing import Optional, Tuple

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch, ConflictError, NotFoundError
from pydantic import BaseModel, Field

from tase.my_logger import logger
from tase.utils import get_timestamp


class SearchMetaData(BaseModel):
    rank: int
    score: float


class BaseDocument(BaseModel):
    _index_name = "base_index_name"
    _mappings = {}

    _to_db_mapping = ['id', 'search_metadata']
    _do_not_update = ['created_at']
    _search_fields = []

    id: Optional[str]

    created_at: int = Field(default_factory=get_timestamp)
    modified_at: int = Field(default_factory=get_timestamp)

    search_metadata: Optional[SearchMetaData]

    def parse_for_db(self) -> Tuple[str, dict]:
        temp_dict = self.dict()
        for key in self._to_db_mapping:
            del temp_dict[key]

        return self.id, temp_dict

    @classmethod
    def parse_from_db(cls, response: ObjectApiResponse):
        if response is None or not len(response.body):
            return None

        body = dict(**response.body['_source'])
        body.update({'id': response.body['_id']})

        return cls(**body)

    @classmethod
    def parse_from_db_hit(cls, hit: dict, rank: int):
        if hit is None or not len(hit) or not len(hit['_source']) or rank is None:
            return None

        body = dict(**hit['_source'])
        body.update({'id': hit['_id']})

        obj = cls(**body)
        obj.search_metadata = SearchMetaData(rank=rank, score=hit.get('_score', None))
        return obj

    def _update_doc_from_old_doc(self, old_doc: 'BaseDocument'):
        for k in self._do_not_update:
            if getattr(self, k, None):
                setattr(self, k, getattr(old_doc, k, None))

        return self

    @classmethod
    def has_index(cls, es: 'Elasticsearch') -> bool:
        index_exists = False
        try:
            es.indices.get(index=cls._index_name)
            index_exists = True
        except NotFoundError as e:
            pass
        except Exception as e:
            logger.exception(e)
        return index_exists

    @classmethod
    def create_index(cls, es: 'Elasticsearch'):
        try:
            es.indices.create(
                index=cls._index_name,
                mappings=cls._mappings,
            )
        except Exception as e:
            pass

    @classmethod
    def get(cls, es: 'Elasticsearch', doc_id: str):
        if es is None:
            return None

        obj = None
        try:
            response = es.get(index=cls._index_name, id=doc_id)
            obj = cls.parse_from_db(response)
        except NotFoundError as e:
            # audio does not exist in the index
            pass
        except Exception as e:
            logger.exception(e)
        return obj

    @classmethod
    def create(cls, es: 'Elasticsearch', document: 'BaseDocument'):
        """
        Creates a document in the index

        :param es: Elasticsearch low-level client
        :param document: The document to insert in the index
        :return: document, successful
        """
        if es is None or document is None:
            return None, False

        if not isinstance(document, BaseDocument):
            raise Exception(f'`document` is not an instance of {BaseDocument.__class__.__name__} class')

        successful = False
        try:
            id, doc = document.parse_for_db()
            if id and doc:
                response = es.create(
                    index=cls._index_name,
                    id=id,
                    document=doc
                )
                successful = True
        except ConflictError as e:
            # Exception representing a 409 status code. Document exists in the index
            logger.exception(e)
        except Exception as e:
            logger.exception(e)

        return document, successful

    @classmethod
    def update(cls, es: 'Elasticsearch', old_document: 'BaseDocument', document: 'BaseDocument'):
        """
        Updates a document in the index

        :param es: Elasticsearch low-level client
        :param old_document: The old document that is already in the index
        :param document: The new document to update in the index
        :return: document, successful
        """
        if es is None or old_document is None or document is None:
            return None, False

        if not isinstance(document, BaseDocument):
            raise Exception(f'`document` is not an instance of {BaseDocument.__class__.__name__} class')

        successful = False
        try:
            id, doc = document._update_doc_from_old_doc(old_document).parse_for_db()
            if id and doc:
                response = es.update(
                    index=cls._index_name,
                    id=id,
                    doc=doc
                )
                successful = True
        except Exception as e:
            logger.exception(e)

        return document, successful

    @classmethod
    def search(
            cls,
            es: 'Elasticsearch',
            query: str,
            from_: int = 0,
            size: int = 50,
    ):
        if es is None or query is None or from_ is None or size is None:
            return None

        db_docs = []
        search_metadata = {
            'duration': None,
            'total_hits': None,
            'total_rel': None,
            'max_score': None,
        }

        try:
            res: 'ObjectApiResponse' = es.search(
                index=cls._index_name,
                from_=from_,
                size=size,
                query={
                    "multi_match": {
                        "query": query,
                        "type": 'best_fields',
                        "minimum_should_match": "60%",
                        "fields": cls._search_fields,
                    },
                }
            )

            hits = res.body['hits']['hits']

            duration = res.meta.duration
            total_hits = res.body['hits']['total']['value']
            total_rel = res.body['hits']['total']['relation']
            max_score = res.body['hits']['max_score']

            search_metadata = {
                'duration': duration,
                'total_hits': total_hits,
                'total_rel': total_rel,
                'max_score': max_score,
            }

            for index, hit in enumerate(hits, start=1):
                db_doc = cls.parse_from_db_hit(hit, len(hits) - index + 1)
                db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        return db_docs, search_metadata
