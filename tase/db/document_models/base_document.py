from typing import Optional

from arango import DocumentInsertError, DocumentRevisionError, DocumentUpdateError
from arango.collection import StandardCollection
from pydantic import BaseModel, Field

from tase.my_logger import logger
from tase.utils import get_timestamp


class BaseDocument(BaseModel):
    _doc_collection_name = "base_document_name"

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]

    created_at: int = Field(default_factory=get_timestamp)
    modified_at: int = Field(default_factory=get_timestamp)

    _from_document_db_mapping = {
        "_id": "id",
        "_key": "key",
        "_rev": "rev",
    }
    _to_document_db_mapping = {
        "id": "_id",
        "key": "_key",
        "rev": "_rev",
    }
    _do_not_update = ["created_at"]

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
    def _from_db(cls, document: dict) -> Optional["dict"]:
        if not len(document):
            return None

        for k, v in BaseDocument._from_document_db_mapping.items():
            if document.get(k, None):
                document[v] = document[k]
                del document[k]
            else:
                document[v] = None

        return document

    def parse_for_db(self) -> dict:
        return self._to_db()

    @classmethod
    def parse_from_db(cls, document: dict):
        if document is None or not len(document):
            return None
        return cls(**cls._from_db(document))

    def _update_from_metadata(self, metadata: dict):
        """
        Update the document's metadata from the `metadata`

        :param metadata: metadata returned from the database transaction
        """
        for k, v in self._from_document_db_mapping.items():
            setattr(self, v, metadata.get(k, None))

    def _update_metadata_from_old_document(self, old_document: "BaseDocument"):
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

    @classmethod
    def create(cls, db: "StandardCollection", doc: "BaseDocument"):
        """
        Insert a document into the database

        :param db: The StandardCollection to use for inserting the document
        :param doc: The document to insert into the database
        :return: self, successful
        """

        if db is None or doc is None:
            return None, False

        successful = False
        try:
            metadata = db.insert(doc.parse_for_db())
            doc._update_from_metadata(metadata)
            successful = True
        except DocumentInsertError as e:
            # Failed to insert the document
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        return doc, successful

    @classmethod
    def update(
        cls, db: "StandardCollection", old_doc: "BaseDocument", doc: "BaseDocument"
    ):
        """
        Update a document in the database

        :param db: The StandardCollection to use for updating the document
        :param old_doc:  The document that is already in the database
        :param doc: The document used for updating the object in the database
        :return: self, successful
        """
        if not isinstance(doc, BaseDocument):
            raise Exception(
                f"`document` is not an instance of {BaseDocument.__class__.__name__} class"
            )

        if db is None or old_doc is None or doc is None:
            return None, False

        successful = False
        try:
            metadata = db.update(
                doc._update_metadata_from_old_document(old_doc).parse_for_db()
            )
            doc._update_from_metadata(metadata)
            successful = True
        except DocumentUpdateError as e:
            # Failed to update document.
            logger.exception(e)
        except DocumentRevisionError as e:
            # The expected and actual document revisions mismatched.
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        return doc, successful

    @classmethod
    def find_by_key(cls, db: "StandardCollection", key: str):
        if db is None or key is None:
            return None

        cursor = db.find({"_key": key})
        if cursor and len(cursor):
            return cls.parse_from_db(cursor.pop())
        else:
            return None
