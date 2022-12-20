import asyncio
from enum import Enum
from itertools import chain
from typing import Dict, Optional, Any, Type, Union, Tuple, TypeVar, List, Generator

from pydantic import BaseModel, Field, ValidationError

from aioarango.api import VertexCollection, EdgeCollection, StandardCollection, AQL, Cursor
from aioarango.enums import IndexType
from aioarango.errors import ArangoServerError, DocumentRevisionMisMatchError, DocumentRevisionMatchError, CursorCountError, CollectionUniqueConstraintViolated
from aioarango.models.index import PersistentIndex
from aioarango.typings import ArangoIndex, Result
from tase.common.utils import get_now_timestamp
from tase.errors import NotSoftDeletableSubclass, NotBaseCollectionDocumentInstance
from tase.my_logger import logger

TBaseCollectionDocument = TypeVar("TBaseCollectionDocument", bound="BaseCollectionDocument")
TBaseCollectionAttributes = TypeVar("TBaseCollectionAttributes", bound="BaseCollectionAttributes")


class ToGraphBaseProcessor(BaseModel):
    @classmethod
    def process(
        cls,
        document: TBaseCollectionAttributes,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        """
        Execute some operations on the attribute value dictionary.

        Parameters
        ----------
        document : TBaseCollectionAttributes
            Document this processing is done for
        attr_value_dict : dict
            Attribute value mapping dictionary to be processed

        Raises
        ------
        Exception
            if there was any error with processing
        """
        raise NotImplementedError


class FromGraphBaseProcessor(BaseModel):
    @classmethod
    def process(
        cls,
        document_class: Type[TBaseCollectionAttributes],
        graph_doc: Dict[str, Any],
    ) -> None:
        """
        Execute some operations on the attribute value dictionary.

        Parameters
        ----------
        document_class : Type[TBaseCollectionAttributes]
            Class of this document. (It's not an instance of the class)
        graph_doc : dict
            Attribute value mapping dictionary to be processed

        Raises
        ------
        Exception
            if there was any error with processing
        """
        raise NotImplementedError


##############################################################################


class ToGraphAttributeMapper(ToGraphBaseProcessor):
    """
    Prepare the attribute value mapping to be saved into the database.
    """

    @classmethod
    def process(
        cls,
        document: TBaseCollectionAttributes,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for obj_attr, graph_doc_attr in document._to_graph_db_mapping.items():
            attr_value = attr_value_dict.get(obj_attr, None)
            if attr_value is not None:
                attr_value_dict[graph_doc_attr] = attr_value
                del attr_value_dict[obj_attr]
            else:
                if obj_attr in attr_value_dict:
                    del attr_value_dict[obj_attr]
                    attr_value_dict[graph_doc_attr] = None


class ToGraphEnumConverter(ToGraphBaseProcessor):
    """
    Convert enum types to their values because `Enum` types cannot be directly saved into ArangoDB.

    """

    @classmethod
    def process(
        cls,
        document: TBaseCollectionAttributes,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for attr_name, attr_value in attr_value_dict.copy().items():
            attr_value = getattr(document, attr_name, None)
            if attr_value:
                if isinstance(attr_value, Enum):
                    attr_value_dict[attr_name] = attr_value.value


class ToGraphNestedConverter(ToGraphBaseProcessor):
    """
    Convert Nested types to their values.

    """

    @classmethod
    def process(
        cls,
        document: TBaseCollectionAttributes,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for attr_name, attr_value in attr_value_dict.copy().items():
            attr_value = getattr(document, attr_name, None)
            if attr_value:
                if isinstance(attr_value, BaseCollectionAttributes):
                    attr_value_dict[attr_name] = attr_value.to_collection()


class FromGraphAttributeMapper(FromGraphBaseProcessor):
    """
    Prepare the attribute value mapping from graph to be converted into a python object.
    """

    @classmethod
    def process(
        cls,
        document_class: Type[TBaseCollectionAttributes],
        graph_doc: Dict[str, Any],
    ) -> None:
        for graph_doc_attr, obj_attr in document_class._from_graph_db_mapping.items():
            attr_value = graph_doc.get(graph_doc_attr, None)
            if attr_value is not None:
                graph_doc[obj_attr] = attr_value
                del graph_doc[graph_doc_attr]
            else:
                graph_doc[obj_attr] = None


################################################################################


class BaseCollectionAttributes(BaseModel):
    _from_graph_db_mapping = {
        "_id": "id",
        "_key": "key",
        "_rev": "rev",
    }

    _to_graph_db_mapping = {
        "id": "_id",
        "key": "_key",
        "rev": "_rev",
    }

    _to_graph_db_base_processors: Optional[Tuple[ToGraphBaseProcessor]] = (
        ToGraphEnumConverter,
        ToGraphAttributeMapper,
        ToGraphNestedConverter,
    )
    _to_graph_db_extra_processors: Optional[Tuple[ToGraphBaseProcessor]] = None

    _from_graph_db_base_processors: Optional[Tuple[FromGraphBaseProcessor]] = (FromGraphAttributeMapper,)
    _from_graph_db_extra_processors: Optional[Tuple[FromGraphBaseProcessor]] = None

    _base_do_not_update_fields: Optional[Tuple[str]] = ("created_at",)
    _extra_do_not_update_fields: Optional[Tuple[str]] = None

    _base_indexes: List[ArangoIndex] = [
        PersistentIndex(
            custom_version=1,
            name="created_at",
            fields=[
                "created_at",
            ],
        ),
        PersistentIndex(
            custom_version=1,
            name="modified_at",
            fields=[
                "modified_at",
            ],
        ),
    ]

    _extra_indexes: Optional[List[ArangoIndex]] = []

    def to_collection(self) -> Optional[Dict[str, Any]]:
        """
        Convert the object to a dictionary to be saved into the ArangoDB.

        Returns
        -------
        dict
            Dictionary mapping attribute names to attribute values

        """
        attr_value_dict = self.dict()

        for attrib_processor in self._to_graph_db_base_processors:
            try:
                attrib_processor.process(self, attr_value_dict)
            except Exception as e:
                logger.exception(e)
                return None

        if self._to_graph_db_extra_processors is not None:
            for doc_processor in self._to_graph_db_extra_processors:
                try:
                    doc_processor.process(self, attr_value_dict)
                except Exception as e:
                    logger.exception(e)
                    return None

        return attr_value_dict

    @classmethod
    def from_collection(
        cls: Type[TBaseCollectionDocument],
        doc: Dict[str, Any],
    ) -> Optional[TBaseCollectionDocument]:
        """
        Convert a database document dictionary to be converted into a python object.

        Parameters
        ----------
        doc : dict
            Dictionary mapping attribute names to attribute values

        Returns
        -------
        TBaseCollectionDocument, optional
            Python object converted from the database document dictionary

        """
        if not doc:
            return None

        for doc_processor in cls._from_graph_db_base_processors:
            try:
                doc_processor.process(cls, doc)
            except Exception as e:
                return None

        if cls._from_graph_db_extra_processors is not None:
            for doc_processor in cls._from_graph_db_extra_processors:
                try:
                    doc_processor.process(cls, doc)
                except Exception as e:
                    return None

        try:
            obj = cls(**doc)
        except ValidationError as e:
            # Attribute value mapping cannot be validated, and it cannot be converted to a python object
            logger.error(f"{cls.__name__} : {e.json()}")
        except Exception as e:
            # todo: check if this happens
            logger.exception(e)
        else:
            return obj

        return None


class BaseCollectionDocument(BaseCollectionAttributes):
    schema_version: int = Field(default=1)

    _collection_name = "base_documents"
    _collection: Optional[Union[VertexCollection, EdgeCollection, StandardCollection]]
    _aql: Optional[AQL]
    _graph_name: Optional[str]

    id: Optional[str]
    key: Optional[str]
    rev: Optional[str]

    created_at: int = Field(default_factory=get_now_timestamp)
    modified_at: int = Field(default_factory=get_now_timestamp)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    async def update_indexes(cls):
        """
        Update the indexes of a collection in the database

        Raises
        ------
        arango.exceptions.IndexCreateError
            If the index creation fails
        """
        current_index_mapping = {}
        for index in await cls._collection.indexes():
            if index.type in (IndexType.PRIMARY, IndexType.EDGE):
                continue

            current_index_mapping[index.name] = index

        new_index_names = [index.name for index in chain(cls._base_indexes, cls._extra_indexes if cls._extra_indexes is not None else [])]
        for old_index in current_index_mapping.values():
            if old_index.name not in new_index_names:
                await cls._collection.delete_index(old_index.id, ignore_missing=True)

        for index in chain(cls._base_indexes, cls._extra_indexes if cls._extra_indexes is not None else []):
            try:
                if index.name not in current_index_mapping:
                    logger.info(f"Adding index `{index.name}` to `{cls._collection.name}` collection")
                    await cls._collection.add_index(index)
                else:
                    if current_index_mapping[index.name].custom_version != index.custom_version:
                        logger.info(f"Updating index `{index.name}` in `{cls._collection.name}` collection")
                        await cls._collection.delete_index(current_index_mapping[index.name].id, ignore_missing=True)
                        await cls._collection.add_index(index)

            except Exception as e:
                temp = index.to_db()
                logger.exception(temp)
                logger.exception(e)

    @classmethod
    async def insert(
        cls: Type[TBaseCollectionDocument],
        doc: TBaseCollectionDocument,
    ) -> Tuple[Optional[TBaseCollectionDocument], bool]:
        """
        Insert an object into the ArangoDB

        Parameters
        ----------
        doc : TBaseCollectionDocument
            Object to inserted into the ArangoDB

        Returns
        -------
        tuple
            Document object with returned metadata from ArangoDB and `True` if the operation was successful,
            otherwise return `None` and `False`.
        """

        if doc is None:
            return None, False

        successful = False
        try:
            graph_doc = doc.to_collection()
            if graph_doc is None:
                return None, False

            metadata = await cls._collection.insert(graph_doc)
            doc._update_metadata(metadata)
        except CollectionUniqueConstraintViolated:
            # A unique constraint in this collection has been violated; document key or an unique index.
            # fixme
            logger.error(f"[CollectionUniqueConstraintViolated] => {doc.id}")
        except ArangoServerError as e:
            # Failed to insert the document
            logger.exception(f"{cls.__name__} : {e}")
        except Exception as e:
            logger.exception(f"{cls.__name__} : {e}")
        else:
            successful = True

        return doc, successful

    @classmethod
    async def get(
        cls: Type[TBaseCollectionDocument],
        doc_key: str,
    ) -> Optional[TBaseCollectionDocument]:
        """
        Get a document in a collection by its `Key`

        Parameters
        ----------
        doc_key : str
            Key of the document in the collection

        Returns
        -------
        TBaseCollectionDocument, optional
            Document matching the specified `Key` if it exists in the collection, otherwise return `None`

        """
        if doc_key is None or not len(doc_key):
            return None

        try:
            graph_doc = await cls._collection.get(doc_key)
            return cls.from_collection(graph_doc)
        except DocumentRevisionMisMatchError as e:
            logger.exception(e)
        except DocumentRevisionMatchError as e:
            logger.exception(e)
        except ArangoServerError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)

        return None

    @classmethod
    async def has(
        cls: Type[TBaseCollectionDocument],
        doc_key: str,
    ) -> Optional[bool]:
        """
        Check if a document exists in the collection.

        Parameters
        ----------
        doc_key : str
            Key of the document in the collection

        Returns
        -------
        bool, optional
            Document matching the specified `Key` if it exists in the collection, otherwise return `None`

        """
        if doc_key is None:
            return None

        try:
            return await cls._collection.has(doc_key)
        except DocumentRevisionMisMatchError as e:
            # If revisions mismatch.
            caught_error = True
            logger.exception(e)
        except DocumentRevisionMatchError as e:
            # If revisions match.
            caught_error = True
            logger.exception(e)
        except ArangoServerError as e:
            # If check fails.
            caught_error = True
            logger.exception(e)
        except Exception as e:
            caught_error = True
            logger.exception(e)

        return None if caught_error else False

    @classmethod
    async def find(
        cls: Type[TBaseCollectionDocument],
        filters: Dict[str, Any],
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        filter_out_soft_deleted: Optional[bool] = None,
    ) -> Generator[TBaseCollectionDocument, None, None]:
        """
        Find all documents that match the given filters.

        Parameters
        ----------
        filters : dict
            Filters to be applied
        offset : int, default: 0
            Number of documents to skip
        limit : int, default: None
            Max number of documents returned
        filter_out_soft_deleted : bool, default: None
            Whether to filter out by soft-deleted documents or not.

        Raises
        ------
        NotSoftDeletableSubclass
            If the document calling this method uses the `filter_out_soft_deleted` argument and is not a subclass of
            `BaseSoftDeletableDocument`.
        """
        if filters is None or not isinstance(filters, dict):
            return

        if filter_out_soft_deleted is not None:
            from tase.db.arangodb.base import BaseSoftDeletableDocument

            if issubclass(cls, BaseSoftDeletableDocument):
                filters.update(
                    {
                        "is_soft_deleted": not filter_out_soft_deleted,
                    }
                )
            else:
                raise NotSoftDeletableSubclass(cls.__name__)

        try:
            async with await cls._collection.find(
                filters,
                skip=offset,
                limit=limit,
            ) as cursor:
                async for graph_doc in cursor:
                    yield cls.from_collection(graph_doc)

        except ValueError as e:
            logger.exception(e)
        except ArangoServerError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)

        return

    @classmethod
    async def find_one(
        cls: Type[TBaseCollectionDocument],
        filters: Dict[str, Any],
        filter_out_soft_deleted: Optional[bool] = None,
    ) -> Optional[TBaseCollectionDocument]:
        """
        Find one document that match the given filters.

        Parameters
        ----------
        filters : dict
            Document filters
        filter_out_soft_deleted : bool, default: None
            Whether to filter out the soft-deleted documents.

        Returns
        -------
        TBaseCollectionDocument, optional
            Document matching given filters if it exists, otherwise return `None`.

        Raises
        ------
        NotSoftDeletableSubclass
            If the document calling this method uses the `filter_out_soft_deleted` argument and is not a subclass of
            `BaseSoftDeletableDocument`.
        """
        async for document in cls.find(
            filters,
            limit=1,
            filter_out_soft_deleted=filter_out_soft_deleted,
        ):
            return document

    async def delete(
        self,
        soft_delete: Optional[bool] = False,
        is_exact_date: Optional[bool] = False,
        deleted_at: Optional[int] = None,
    ) -> bool:
        """
        Delete / Soft Delete the document in ArangoDB

        Parameters
        ----------
        soft_delete : bool, default: False
            If this parameter is set to `True`, the document will not be deleted, but, it will be marked as deleted.
        is_exact_date : bool, default: False
            Whether the time of deletion is exact or an estimation.
        deleted_at : int, default: None
            Timestamp of deletion.

        Returns
        -------
        bool
            Whether the operation was successful or not


        Raises
        ------
        NotSoftDeletableSubclass
            If the document calling this method uses the `filter_out_soft_deleted` argument and is not a subclass of
            `BaseSoftDeletableDocument`.
        """
        if soft_delete:
            from tase.db.arangodb.base import BaseSoftDeletableDocument

            if issubclass(type(self), BaseSoftDeletableDocument):
                self_copy = self.copy(deep=True)
                self_copy.is_soft_deleted = True
                self_copy.is_soft_deleted_time_precise = is_exact_date
                self_copy.soft_deleted_at = get_now_timestamp() if deleted_at is None else deleted_at
                return await self.update(self_copy, reserve_non_updatable_fields=False)
            else:
                raise NotSoftDeletableSubclass(self.__class__.__name__)
        else:
            return await self.delete_document(self)

    @classmethod
    async def delete_document(
        cls: Type[TBaseCollectionDocument],
        doc: Union[TBaseCollectionDocument, str],
    ) -> bool:
        """
        Delete an object in ArangoDB

        Parameters
        ----------
        doc : TBaseCollectionDocument or str
            Object to inserted into the ArangoDB or the Key of the document to be deleted

        Returns
        -------
        bool
            Whether the operation was successful or not
        """

        if doc is None:
            return False

        successful = False
        key = doc.key if isinstance(doc, BaseCollectionDocument) else doc
        try:
            successful = await cls._collection.delete(
                key,
                ignore_missing=True,
                check_for_revisions_match=False,  # fixme
            )
        except DocumentRevisionMisMatchError as e:
            # The expected and actual document revisions mismatched.
            logger.exception(f"{cls.__name__} : {e}")
        except ArangoServerError as e:
            # Failed to delete the document
            logger.exception(f"{cls.__name__} : {e}")
        except Exception as e:
            logger.exception(f"{cls.__name__} : {e}")
        return successful

    async def update(
        self: TBaseCollectionDocument,
        doc: TBaseCollectionDocument,
        reserve_non_updatable_fields: bool = True,
        check_for_revisions_match: Optional[bool] = True,
        wait_for_sync: Optional[bool] = None,
        retry_on_failure: bool = True,
        run_depth: int = 1,
    ) -> bool:
        """
        Update an object in the database

        Parameters
        ----------
        doc: TBaseCollectionDocument
            Document used for updating the object in the database
        reserve_non_updatable_fields : bool
            Whether to keep the non-updatable fields from the old document or not
        check_for_revisions_match : bool, default: True
            If set to True, revision of current document (if given) is compared against the revision of target document. Default to `True`.
        wait_for_sync : bool, default: None
            sync: Block until operation is synchronized to disk. Default to `None`
        retry_on_failure : bool, default : True
            Whether to retry the operation if it fails due to `revision` mismatch
        run_depth : int
            Depth of running the function. stop and return False after 10 runs.

        Returns
        -------
        bool
            Whether the update was successful or not

        """
        if not isinstance(doc, BaseCollectionDocument):
            raise NotBaseCollectionDocumentInstance(doc.__class__.__name__)

        if doc is None:
            return False

        if retry_on_failure and run_depth > 10:
            logger.error(f"{self.__class__.__name__}: `{self.key}` : failed after 10 retries")
            # stop if the update is retried for 10 times
            return False

        successful = False
        try:
            if reserve_non_updatable_fields:
                graph_doc = doc._update_metadata_from_old_document(self)._update_non_updatable_fields(self).to_collection()
            else:
                graph_doc = doc._update_metadata_from_old_document(self).to_collection()
            if graph_doc is None:
                return False

            graph_doc["modified_at"] = get_now_timestamp()

            metadata = await self._collection.update(
                graph_doc,
                check_for_revisions_match=check_for_revisions_match,
                wait_for_sync=wait_for_sync,
            )
            doc._update_metadata(metadata)
            self.__dict__.update(doc.__dict__)
            # copy_attrs_from_new_document(self, doc)
        except DocumentRevisionMisMatchError as e:
            logger.error(f"{self.__class__.__name__}: `{self.key}` : DocumentRevisionError")
            # The expected and actual document revisions mismatched.
            successful = await self._retry_update(
                check_for_revisions_match,
                doc,
                reserve_non_updatable_fields,
                retry_on_failure,
                run_depth,
                successful,
                wait_for_sync,
            )
        except ArangoServerError as e:
            # Failed to update document.
            logger.error(f"{self.__class__.__name__}: `{self.key}` : DocumentUpdateError")
            # The expected and actual document revisions mismatched.
            successful = await self._retry_update(
                check_for_revisions_match,
                doc,
                reserve_non_updatable_fields,
                retry_on_failure,
                run_depth,
                successful,
                wait_for_sync,
            )
        except Exception as e:
            logger.exception(f"{self.__class__.__name__} : {e}")
        else:
            successful = True
        return successful

    async def _retry_update(
        self,
        check_for_revisions_match: bool,
        doc: TBaseCollectionDocument,
        reserve_non_updatable_fields: bool,
        retry_on_failure: bool,
        run_depth: int,
        successful: bool,
        wait_for_sync: bool,
    ):
        if retry_on_failure:
            logger.error(f"Retry #{run_depth}")
            # todo: sleep for a while before retrying
            await asyncio.sleep(run_depth * 20 / 1000)

            latest_doc = await self.get(self.key)
            if latest_doc is not None:
                successful = await latest_doc.update(
                    doc,
                    reserve_non_updatable_fields=reserve_non_updatable_fields,
                    check_for_revisions_match=check_for_revisions_match,
                    wait_for_sync=wait_for_sync,
                    retry_on_failure=retry_on_failure,
                    run_depth=run_depth + 1,
                )
                if successful:
                    logger.error(f"Success after retry #{run_depth}")
                    self.__dict__.update(latest_doc.__dict__)
        return successful

    @classmethod
    async def replace(
        cls: Type[TBaseCollectionDocument],
        old_doc: TBaseCollectionDocument,
        doc: TBaseCollectionDocument,
    ) -> Tuple[Optional[TBaseCollectionDocument], bool]:
        """
        Replace an object in the database with the new one

        Parameters
        ----------
        old_doc : TBaseCollectionDocument
            Document that is already in the database
        doc: TBaseCollectionDocument
            Document used for replacing the object in the database

        Returns
        -------
        tuple
            Replaced document and whether the operation was successful.

        Raises
        ------
        Exception
            If the new document is not instance of `BaseCollectionDocument` class.
        """
        if not isinstance(doc, BaseCollectionDocument):
            raise NotBaseCollectionDocumentInstance(doc.__class__.__name__)

        if old_doc is None or doc is None:
            return None, False

        successful = False
        try:
            graph_doc = doc._update_metadata_from_old_document(old_doc)._update_non_updatable_fields(old_doc).to_collection()
            if graph_doc is None:
                return None, False

            metadata = await cls._collection.replace(graph_doc)
            doc._update_metadata(metadata)
        except DocumentRevisionMisMatchError as e:
            # The expected and actual document revisions mismatched.
            logger.exception(f"{cls.__name__} : {e}")
        except ArangoServerError as e:
            # Failed to replace document.
            logger.exception(f"{cls.__name__} : {e}")
        except Exception as e:
            logger.exception(f"{cls.__name__} : {e}")
        else:
            successful = True

        return doc, successful

    def _update_metadata(
        self,
        metadata: Dict[str, str],
    ) -> None:
        """
        Update a document's metadata from the `metadata` parameter

        Parameters
        ----------
        metadata : dict
            Metadata returned from the database query

        """
        for k, v in self._from_graph_db_mapping.items():
            setattr(self, v, metadata.get(k, None))

    def _update_metadata_from_old_document(
        self,
        old_doc: TBaseCollectionDocument,
    ) -> TBaseCollectionDocument:
        """
        Update the metadata of this document from an old document metadata

        Parameters
        ----------
        old_doc : TBaseCollectionDocument
            The document to get the metadata from

        Returns
        -------
        TBaseCollectionDocument
            Updated document
        """
        for field_name in self._to_graph_db_mapping.keys():
            setattr(self, field_name, getattr(old_doc, field_name, None))

        return self

    def _update_non_updatable_fields(
        self,
        old_doc: TBaseCollectionDocument,
    ) -> TBaseCollectionDocument:
        """
        Update the non-updatable field values of a document from an old document

        Parameters
        ----------
        old_doc : TBaseCollectionDocument
            Document to update the fields from

        Returns
        -------
        TBaseCollectionDocument
            Updated document

        """
        for field_name in self._base_do_not_update_fields:
            setattr(self, field_name, getattr(old_doc, field_name, None))

        if self._extra_do_not_update_fields is not None:
            for field_name in self._extra_do_not_update_fields:
                setattr(self, field_name, getattr(old_doc, field_name, None))

        return self

    @classmethod
    async def execute_query(
        cls: Type[TBaseCollectionDocument],
        query: str,
        bind_vars: Dict[str, Any],
        ttl: Optional[int] = None,
        batch_size: Optional[int] = 1000,
    ) -> Result[Cursor]:
        """
        Execute a query and return a `Cursor` object if did not catch any errors, otherwise, return `None`.

        Parameters
        ----------
        query : str
            Query string to execute
        bind_vars : dict
            Dictionary of variables to be bound to the query before running
        ttl : int, optional
            The time-to-live for the cursor (in seconds). If the result set is small enough
            (less than or equal to **batch_size**) then results are returned right away.
            Otherwise, they are stored in memory and will be accessible via the cursor with
            respect to the ttl. The cursor will be removed on the server automatically
            after the specified amount of time. This is useful to ensure garbage collection
            of cursors that are not fully fetched by clients. If not set, a server-defined
            value will be used (default: `30` seconds).
        batch_size : int, default : 1000
            Maximum number of result documents to be transferred from
            the server to the client in one roundtrip. If this attribute is
            not set, a server-controlled default value will be used. A **batch_size** value of
            `0` is disallowed.
        Returns
        -------
        Result[Cursor]
            `Cursor` object if successful, otherwise, return `None`.

        """
        try:
            if "@graph_name" in query:
                bind_vars["graph_name"] = cls._graph_name

            cursor = await cls._aql.execute(
                query,
                bind_vars=bind_vars,
                count=True,
                ttl=ttl,
                batch_size=batch_size,
            )
        except CursorCountError as e:
            logger.error(query)
            logger.exception(e)
        except ArangoServerError as e:
            logger.error(query)
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        else:
            return cursor

        return Cursor(
            cls._aql._connection,
            cls._aql._executor,
            {},
        )

    ########################################################################
    @classmethod
    def parse(
        cls: Type[TBaseCollectionDocument],
        *args,
        **kwargs,
    ) -> Optional[TBaseCollectionDocument]:
        """
        Parse a subclass of `BaseCollectionDocument` document from given arguments and keyword arguments and return
        parsed `BaseCollectionDocument` if successful, otherwise return `None`.

        Parameters
        ----------
        args : tuple
            List of arguments
        kwargs : dict, optional
            Dictionary of keyword arguments

        Returns
        -------
        TBaseCollectionDocument, optional
            Document object if parsing was successful, otherwise, return `None`.

        Raises
        ------
        NotImplementedError
            If the `class` calling this or any of superclasses haven't implemented this method.
        """
        raise NotImplementedError

    @classmethod
    def parse_key(
        cls: Type[TBaseCollectionDocument],
        *args,
        **kwargs,
    ) -> Optional[str]:
        """
        Parse a key from the given arguments and keyword arguments and return a key if successful, otherwise,
        return `None`.

        Parameters
        ----------
        args : tuple
            List of arguments
        kwargs : dict, optional
            List of keyword arguments

        Returns
        -------
        str, optional
            Key string if parsing was successful, otherwise, return `None`.

        Raises
        ------
        NotImplementedError
            If the `class` calling this or any of superclasses haven't implemented this method.
        """
        raise NotImplementedError
