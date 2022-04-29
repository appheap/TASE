from typing import Optional

from pydantic import BaseModel, Field

from tase.utils import get_timestamp


class BaseDocument(BaseModel):
    _doc_collection_name = "base_document_name"

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]

    created_at: int = Field(default_factory=get_timestamp)
    modified_at: int = Field(default_factory=get_timestamp)

    _from_document_db_mapping = {
        '_id': 'id',
        '_key': 'key',
        '_rev': 'rev',
    }
    _to_document_db_mapping = {
        'id': '_id',
        'key': '_key',
        'rev': '_rev',
    }
    _do_not_update = ['created_at']

    def _to_db(self) -> dict:
        temp_dict = self.dict()
        for k, v in self._to_document_db_mapping.items():
            if temp_dict.get(k, None):
                temp_dict[v] = temp_dict[k]
                del temp_dict[k]
            else:
                del temp_dict[k]
                temp_dict[v] = None

        return temp_dict

    @classmethod
    def _from_db(cls, vertex: dict) -> Optional['dict']:
        if not len(vertex):
            return None

        for k, v in BaseDocument._from_document_db_mapping.items():
            if vertex.get(k, None):
                vertex[v] = vertex[k]
                del vertex[k]
            else:
                vertex[v] = None

        return vertex

    def parse_for_db(self) -> dict:
        return self._to_db()

    @classmethod
    def parse_from_db(cls, vertex: dict):
        if vertex is None or not len(vertex):
            return None
        return cls(**cls._from_db(vertex))

    def _update_from_metadata(self, metadata: dict):
        """
        Update the document's metadata from the `metadata`

        :param metadata: metadata returned from the database transaction
        """
        for k, v in self._from_document_db_mapping.items():
            setattr(self, v, metadata.get(k, None))

    def _update_metadata_from_old_document(self, old_document: 'BaseDocument'):
        """
        Updates the metadata of this document from another document metadata
        :param old_document: The vertex to get the metadata from
        :return: self
        """
        for k in self._to_document_db_mapping.keys():
            setattr(self, k, getattr(old_document, k, None))

        for k in self._do_not_update:
            setattr(self, k, getattr(old_document, k, None))

        return self
