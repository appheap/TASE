from __future__ import annotations

import asyncio
import collections
from enum import Enum
from typing import Optional, Tuple, TypeVar, Dict, Any, Type, List, Deque

import elasticsearch
from elastic_transport import ObjectApiResponse
from elasticsearch import ConflictError, NotFoundError, AsyncElasticsearch
from pydantic import BaseModel, Field, ValidationError

from tase.common.utils import get_now_timestamp
from tase.db.arangodb.helpers import ElasticQueryMetadata
from tase.db.helpers import SearchMetaData
from tase.errors import NotSoftDeletableSubclass
from tase.my_logger import logger

TBaseDocument = TypeVar("TBaseDocument", bound="BaseDocument")


class ToDocumentBaseProcessor(BaseModel):
    @classmethod
    def process(
        cls,
        document: TBaseDocument,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        """
        Execute some operations on the attribute value dictionary.

        Parameters
        ----------
        document : TBaseDocument
            Document this processing is done for
        attr_value_dict : dict
            Attribute value mapping dictionary to be processed

        Raises
        ------
        Exception
            if there was any error with processing
        """
        raise NotImplementedError


class FromDocumentBaseProcessor(BaseModel):
    @classmethod
    def process(
        cls,
        document_class: Type[TBaseDocument],
        body: dict,
        response: Optional[ObjectApiResponse],
        hit: Optional[dict],
    ) -> None:
        """
        Execute some operations on the attribute value dictionary.

        Parameters
        ----------
        document_class : Type[TBaseDocument]
            Class of this document. (It's not an instance of the class)
        body : dict
            Dictionary to put the new attributes into
        response : ObjectApiResponse, optional
            Attribute value mapping dictionary to be processed
        hit : dict, optional
            Hit dictionary from the search

        Raises
        ------
        Exception
            if there was any error with processing
        """
        raise NotImplementedError


##########################################################################################
class ToDocumentAttributeMapper(ToDocumentBaseProcessor):
    """
    Prepare the attribute value mapping to be saved into the database.
    """

    @classmethod
    def process(
        cls,
        document: TBaseDocument,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for obj_attr in document.__to_db_mapping__:
            del attr_value_dict[obj_attr]


class ToDocumentEnumConverter(ToDocumentBaseProcessor):
    """
    Convert enum types to their values because `Enum` types cannot be directly saved into ElasticSearch.

    """

    @classmethod
    def process(
        cls,
        document: TBaseDocument,
        attr_value_dict: Dict[str, Any],
    ) -> None:
        for attr_name, attr_value in attr_value_dict.copy().items():
            attr_value = getattr(document, attr_name, None)
            if attr_value:
                if isinstance(attr_value, Enum):
                    attr_value_dict[attr_name] = attr_value.value


class FromDocumentAttributeMapper(FromDocumentBaseProcessor):
    """
    Prepare the attribute value mapping from graph to be converted into a python object.
    """

    @classmethod
    def process(
        cls,
        document_class: Type[TBaseDocument],
        body: dict,
        response: Optional[ObjectApiResponse],
        hit: Optional[dict],
    ) -> None:
        if body is None or (response is None and hit is None):
            return

        if response is not None:
            body.update(**response.body["_source"])
            body.update({"id": response.body["_id"]})
        else:
            body.update(**hit["_source"])
            body.update({"id": hit["_id"]})


##########################################################################################


class BaseDocument(BaseModel):
    schema_version: int = Field(default=1)

    __es__: Optional[AsyncElasticsearch]

    __index_name__ = "base_index_name"
    __mappings__ = {}

    __to_db_mapping__ = ("id", "search_metadata")
    __search_fields__: List[str] = []

    __to_index_base_processors__: Optional[Tuple[ToDocumentBaseProcessor]] = (
        ToDocumentEnumConverter,
        ToDocumentAttributeMapper,
    )
    __to_index_processors__: Optional[Tuple[ToDocumentBaseProcessor]] = None

    __from_index_base_processors__: Optional[Tuple[FromDocumentBaseProcessor]] = (FromDocumentAttributeMapper,)
    __from_index_processors__: Optional[Tuple[FromDocumentBaseProcessor]] = None

    __base_non_updatable_fields__: Optional[Tuple[str]] = ("created_at",)
    __non_updatable_fields__: Optional[Tuple[str]] = None

    id: Optional[str]

    created_at: int = Field(default_factory=get_now_timestamp)
    modified_at: int = Field(default_factory=get_now_timestamp)

    search_metadata: Optional[SearchMetaData]

    def to_index(self) -> Tuple[Optional[str], Optional[dict]]:
        """
        Convert the object to a dictionary to be saved into the ElasticSearch.

        Returns
        -------
        tuple
            Tuple of the document ID and dictionary mapping attribute names to attribute values

        """
        attr_value_dict = self.dict()

        for attrib_processor in self.__to_index_base_processors__:
            try:
                attrib_processor.process(self, attr_value_dict)
            except Exception as e:
                return None, None

        if self.__to_index_processors__ is not None:
            for doc_processor in self.__to_index_processors__:
                try:
                    doc_processor.process(self, attr_value_dict)
                except Exception as e:
                    return None, None

        return self.id, attr_value_dict

    @classmethod
    def from_index(
        cls,
        response: Optional[ObjectApiResponse] = None,
        hit: Optional[dict] = None,
        rank: Optional[int] = None,
    ) -> Optional[TBaseDocument]:
        """
        Convert a database document dictionary to be converted into a python object.

        Parameters
        ----------
        response : ObjectApiResponse, optional
            Attribute value mapping dictionary to be processed
        hit : dict, optional
            Hit dictionary from the search
        rank : int, optional
            Rank of the hit in the query

        Returns
        -------
        TBaseDocument, optional
            Python object converted from the database document dictionary

        Raises
        ------
        ValueError
            If `response` or `hit` parameter is not passed to this function or both of them are None
        """
        is_hit = False
        if response is not None:
            if not len(response.body):
                return None
        elif hit is not None:
            if not len(hit) or not len(hit["_source"]) or rank is None:
                return None

            is_hit = True
        else:
            raise ValueError("either `response` or `hit` parameter must be passed to this method")

        body = dict()
        for doc_processor in cls.__from_index_base_processors__:
            try:
                doc_processor.process(cls, body, response, hit)
            except Exception as e:
                return None

        if cls.__from_index_processors__ is not None:
            for doc_processor in cls.__from_index_processors__:
                try:
                    doc_processor.process(cls, body, response, hit)
                except Exception as e:
                    return None

        try:
            obj = cls(**body)
        except ValidationError as e:
            # Attribute value mapping cannot be validated, and it cannot be converted to a python object
            logger.debug(e.json())
        except Exception as e:
            # todo: check if this happens
            logger.exception(e)
        else:
            if is_hit:
                obj.search_metadata = SearchMetaData(
                    rank=rank,
                    score=hit.get("_score", None) or 0.0,
                )
            return obj

        return None

    def _update_non_updatable_fields(
        self,
        old_doc: TBaseDocument,
    ) -> TBaseDocument:
        """
        Update the non-updatable field values of a document from an old document

        Parameters
        ----------
        old_doc : TBaseDocument
            Document to update the fields from

        Returns
        -------
        TBaseDocument
            Updated document

        """
        for field_name in self.__base_non_updatable_fields__:
            setattr(self, field_name, getattr(old_doc, field_name, None))

        if self.__non_updatable_fields__ is not None:
            for field_name in self.__non_updatable_fields__:
                setattr(self, field_name, getattr(old_doc, field_name, None))

        return self

    @classmethod
    async def has_index(
        cls,
    ) -> bool:
        """
        Check if an index exists in the ElasticSearch.

        Returns
        -------
        bool
            Whether the Index exists in the ElasticSearch or not

        """
        index_exists = False
        try:
            await cls.__es__.indices.get(index=cls.__index_name__)
            index_exists = True
        except NotFoundError as e:
            index_exists = False
        except Exception as e:
            index_exists = False
            logger.exception(e)
        return index_exists

    @classmethod
    async def create_index(
        cls,
    ) -> bool:
        """
        Create the index in the ElasticSearch

        Returns
        -------
        bool
            Whether the index was created or not
        """
        try:
            await cls.__es__.indices.create(
                index=cls.__index_name__,
                mappings=cls.__mappings__,
            )
        except Exception as e:
            raise e
        else:
            return True

    @classmethod
    async def get(
        cls,
        doc_id: str,
    ) -> Optional[TBaseDocument]:
        """
        Get a document in a collection by its `ID`

        Parameters
        ----------
        doc_id : str
            ID of the document in the index

        Returns
        -------
        TBaseDocument, optional
            Document matching the specified `ID` if it exists in the index, otherwise return `None`

        """
        obj = None
        try:
            response = await cls.__es__.get(
                index=cls.__index_name__,
                id=doc_id,
            )
            obj = cls.from_index(response=response)
        except NotFoundError as e:
            # audio does not exist in the index
            pass
        except ValueError as e:
            # happen when the `hit` is None
            pass
        except Exception as e:
            logger.exception(f"{cls.__name__} : {e}")
        return obj

    @classmethod
    async def create(
        cls: Type[TBaseDocument],
        document: TBaseDocument,
    ) -> Tuple[Optional[TBaseDocument], bool]:
        """
        Insert an object into the ElasticSearch

        Parameters
        ----------
        document : TBaseDocument
            Object to inserted into the ElasticSearch

        Returns
        -------
        tuple
            Document object with returned metadata from ElasticSearch and `True` if the operation was successful,
            otherwise return `None` and `False`.
        """
        if document is None:
            return None, False

        if not isinstance(document, BaseDocument):
            raise Exception(f"`document` is not an instance of {BaseDocument.__class__.__name__} class")

        successful = False
        try:
            id, doc = document.to_index()
            if id and doc:
                response = await cls.__es__.create(
                    index=cls.__index_name__,
                    id=id,
                    refresh=False,
                    document=doc,
                )
                successful = True
        except ConflictError as e:
            # Exception representing a 409 status code. Document exists in the index
            pass
            # logger.exception(f"{cls.__name__} : {e}")
        except Exception as e:
            logger.exception(f"{cls.__name__} : {e}")

        return document, successful

    async def delete(
        self,
        soft_delete: Optional[bool] = False,
        is_exact_date: Optional[bool] = False,
        deleted_at: Optional[int] = None,
    ) -> bool:
        """
        Remove a document from the index.

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
            Whether the operation was successful or not.
        """
        if not self.id:
            return False

        try:
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
                resp = await self.__es__.delete(
                    index=self.__index_name__,
                    id=self.id,
                    refresh=False,
                )
        except Exception as e:
            logger.exception(e)
        else:
            return True

        return False

    async def update(
        self,
        document: TBaseDocument,
        reserve_non_updatable_fields: bool = True,
        retry_on_failure: bool = True,
        retry_on_conflict: Optional[bool] = None,
        run_depth: int = 1,
    ) -> bool:
        """
        Update a document in the database

        Parameters
        ----------
        document : TBaseDocument
            Document used for updating the old document in the database.
        reserve_non_updatable_fields : bool, default: True
            Whether to keep the non-updatable fields from the old document or not.
        retry_on_failure : bool, default : True
            Whether to retry the operation if it fails due to `revision` mismatch.
        retry_on_conflict : bool, optional
            Whether to retry the api call if it fails due to `revision` mismatch.
        run_depth : int
            Depth of running the function. stop and return False after 10 runs.

        Returns
        -------
        bool
            Whether the update was successful or not

        """
        if document is None:
            return False

        if not isinstance(document, BaseDocument):
            raise Exception(f"`document` is not an instance of {BaseDocument.__class__.__name__} class")

        if retry_on_failure and run_depth > 10:
            logger.error(f"{self.__class__.__name__}: `{self.id}` : failed after 10 retries")
            # stop if the update is retried for 10 times
            return False

        successful = False
        try:
            if reserve_non_updatable_fields:
                id, doc = document._update_non_updatable_fields(self).to_index()
            else:
                id, doc = document.to_index()

            if id and doc:
                doc["modified_at"] = get_now_timestamp()

                response = await self.__es__.update(
                    index=self.__index_name__,
                    id=id,
                    refresh=False,
                    doc=doc,
                    retry_on_conflict=5 if retry_on_conflict else None,
                )
                self.__dict__.update(document.__dict__)
        except elasticsearch.ConflictError as e:
            logger.error(f"{self.__class__.__name__}: `{self.id}` : elasticsearch.ConflictError")
            if retry_on_failure:
                logger.error(f"Retry #{run_depth}")
                # todo: sleep for a while before retrying
                await asyncio.sleep(run_depth * 20 / 1000)

                latest_doc = await self.get(self.id)
                if latest_doc is not None:
                    successful = await latest_doc.update(
                        document,
                        reserve_non_updatable_fields=reserve_non_updatable_fields,
                        retry_on_failure=retry_on_failure,
                        run_depth=run_depth + 1,
                    )
                    if successful:
                        self.__dict__.update(latest_doc.__dict__)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__} : {e}")
        else:
            successful = True

        return successful

    @classmethod
    async def search(
        cls,
        query: str,
        from_: int = 0,
        size: int = 10,
        filter_by_valid_for_inline_search: Optional[bool] = True,
    ) -> Tuple[Optional[Deque[TBaseDocument]], Optional[ElasticQueryMetadata]]:
        """
        Search among the documents with the given query

        Parameters
        ----------
        query : str
            Query string to search for
        from_ : int, default : 0
            Number of documents to skip in the query
        size : int, default : 10
            Number of documents to return
        filter_by_valid_for_inline_search : bool, default: True
            Whether to filter documents by the validity to be shown in inline search of telegram


        Returns
        -------
        tuple
            List of documents matching the query alongside the query metadata

        """
        if query is None or from_ is None or size is None:
            return None, None

        db_docs = collections.deque()
        try:
            res: ObjectApiResponse = await cls.__es__.search(
                index=cls.__index_name__,
                from_=from_,
                size=size,
                track_total_hits=False,
                query=cls.get_query(query, filter_by_valid_for_inline_search),
                sort=cls.get_sort(),
            )

            hits = res.body["hits"]["hits"]

            duration = res.meta.duration
            try:
                total_hits = res.body["hits"]["total"]["value"] or 0
            except KeyError:
                total_hits = None
            try:
                total_rel = res.body["hits"]["total"]["relation"]
            except KeyError:
                total_rel = None
            max_score = res.body["hits"]["max_score"] or 0

            query_metadata = {
                "duration": duration,
                "total_hits": total_hits,
                "total_rel": total_rel,
                "max_score": max_score,
            }

            query_metadata = ElasticQueryMetadata.parse(query_metadata)

            for index, hit in enumerate(hits, start=1):
                try:
                    db_doc = cls.from_index(
                        hit=hit,
                        rank=index,
                    )
                except ValueError:
                    # fixme: happens when the `hit` is None
                    pass
                else:
                    db_docs.append(db_doc)

        except Exception as e:
            logger.exception(e)

        else:
            return db_docs, query_metadata

        return None, None

    @classmethod
    def get_query(
        cls,
        query: Optional[str],
        filter_by_valid_for_inline_search: Optional[bool] = True,
    ) -> dict:
        """
        Get the query for this index

        Parameters
        ----------
        query : str, optional
            Query string to search for
        filter_by_valid_for_inline_search : bool, default : True
            Whether to filter documents by the validity to be shown in inline search of telegram

        Returns
        -------
        dict
            Dictionary defining how the query should be made

        """
        return {
            "multi_match": {
                "query": query,
                "fuzziness": "AUTO",
                "type": "best_fields",
                "minimum_should_match": "60%",
                "fields": cls.__search_fields__,
            },
        }

    @classmethod
    def get_sort(cls) -> Optional[dict]:
        """
        Get sort dictionary for this query

        Returns
        -------
        dict, optional
            Dictionary defining how the query results should be sorted
        """
        return None

    ######################################################################
    @classmethod
    def parse(
        cls: Type[TBaseDocument],
        *args,
        **kwargs,
    ) -> Optional[TBaseDocument]:
        """
        Parse a subclass of `BaseDocument` document from given arguments and keyword arguments

        Parameters
        ----------
        args : tuple
            List of arguments
        kwargs : dict, optional
            Dictionary of keyword arguments

        Returns
        -------
        TBaseDocument, optional
            Document object if parsing was successful, otherwise, return `None`.

        Raises
        ------
        NotImplementedError
            If the `class` calling this or any of superclasses haven't implemented this method.
        """
        raise NotImplementedError

    @classmethod
    def parse_id(
        cls: Type[TBaseDocument],
        *args,
        **kwargs,
    ) -> Optional[str]:
        """
        Parse an ID from the given arguments and keyword arguments

        Parameters
        ----------
        args : tuple
            List of arguments
        kwargs : dict, optional
            List of keyword arguments

        Returns
        -------
        str, optional
            ID string if parsing was successful, otherwise, return `None`.

        Raises
        ------
        NotImplementedError
            If the `class` calling this or any of superclasses haven't implemented this method.
        """
        raise NotImplementedError
