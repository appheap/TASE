from typing import Optional, Tuple

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch, ConflictError, NotFoundError
from pydantic import BaseModel, Field

from tase.my_logger import logger
from tase.utils import get_timestamp


class BaseDocument(BaseModel):
    _index_name = "base_index_name"

    _to_db_mapping = ['id']
    _do_not_update = ['created_at']

    id: Optional[str]

    created_at: int = Field(default_factory=get_timestamp)
    modified_at: int = Field(default_factory=get_timestamp)

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

    def _update_doc_from_old_doc(self, old_doc: 'BaseDocument'):
        for k in self._do_not_update:
            if getattr(self, k, None):
                setattr(self, k, getattr(old_doc, k, None))

        return self

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
