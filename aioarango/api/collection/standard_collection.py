from typing import Union, Optional

from .base_collection import BaseCollection
from ...api_methods import DocumentsMethods
from ...connection import Connection
from ...enums import OverwriteMode
from ...errors import ArangoServerError, ErrorType
from ...errors.server import DocumentRevisionMisMatchError, DocumentRevisionMatchError, CollectionUniqueConstraintViolated
from ...executor import API_Executor
from ...typings import Json, Result


class StandardCollection(BaseCollection):
    """Standard ArangoDB collection API wrapper."""

    __slots__ = [
        "_connection",
        "_executor",
        "_collections_api",
        "_index_api",
        "_documents_api",
        "_name",
        "_id_prefix",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
        name: str,
    ):
        super(StandardCollection, self).__init__(
            connection=connection,
            executor=executor,
            name=name,
        )

        self._documents_api = DocumentsMethods(connection=connection, executor=executor)

    def __repr__(self) -> str:
        return f"<StandardCollection {self.name}>"

    async def get(
        self,
        document: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        check_for_revisions_mismatch: Optional[bool] = None,
        allow_dirty_read: bool = False,
    ) -> Result[Optional[Json]]:
        """
        Return a document.

        Parameters
        ----------
        document : str or Json
            Document ID, key or body.
        revision : str, default : None
            Document revision to check. Overrides the value of "_rev" field in `document` if present.
        check_for_revisions_match : bool, default : None
            The given revision and the document revision in the database must match.
        check_for_revisions_mismatch : bool, default : None
            The given revision and the document revision in the database must not match.
        allow_dirty_read : bool, default : False
            Whether to allow reads from followers in a cluster.

        Returns
        -------
        Json, optional
            Document, or None if not found.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.server.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.server.DocumentRevisionMatchError
            If revisions match.
        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        try:
            response = await self._documents_api.read_document(
                collection_name=self.name,
                id_prefix=self.id_prefix,
                document=document,
                revision=revision,
                check_for_revisions_match=check_for_revisions_match,
                check_for_revisions_mismatch=check_for_revisions_mismatch,
                allow_dirty_read=allow_dirty_read,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND:
                return None

            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.response.status_code == 304:  # error_code is None in this case
                raise DocumentRevisionMatchError(e.response, e.request)
        else:
            return response

    async def insert(
        self,
        document: Union[str, Json],
        return_new: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
        overwrite: bool = False,
        return_old: bool = False,
        overwrite_mode: Optional[OverwriteMode] = None,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = None,
    ) -> Result[Union[bool, Json]]:
        """
        Insert a new document.

        Parameters
        ----------
        document : str or Json
            Document ID, key or body.
        return_new : bool, default : False
            Include body of the new document in the returned metadata. Ignored if parameter silent is set to True.
        sync : bool, default : False
            Wait until the new documents have been synced to disk.
        silent : bool, default : False
            If set to True, no document metadata is returned. This can be used to save resources.
        overwrite : bool, default : False
            If set to True, operation does not fail on duplicate key and existing document is overwritten (replace-insert).
        return_old : bool, default : False
            Include body of the old document if overwritten. Ignored if parameter `silent` is set to True. Only available if the `overwrite` option is used.
        overwrite_mode : OverwriteMode, default : None
            Overwrite behavior used when the document key exists already. Implicitly sets the value of parameter `overwrite`.
        keep_none : bool, default : None
            If set to True, fields with value None are retained in the document. Otherwise, they are removed completely. Applies only when `overwrite_mode` is set to "update" (update-insert).
        merge : bool, default : None
            If set to True (default), sub-dictionaries are merged instead of the new one overwriting the old one. Applies only when `overwrite_mode` is set to "update" (update-insert).

        Returns
        -------
        bool | Json
            Document metadata (e.g. document key, revision) or `True` if parameter **silent** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body.
        aioarango.errors.server.CollectionUniqueConstraintViolated
            If a unique constraint of the collection is violated.
        aioarango.errors.ArangoServerError
            If insert fails.
        """
        try:
            response = await self._documents_api.create_document(
                collection_name=self.name,
                id_prefix=self.id_prefix,
                document=document,
                return_new=return_new,
                sync=sync,
                silent=silent,
                overwrite=overwrite,
                return_old=return_old,
                overwrite_mode=overwrite_mode,
                keep_none=keep_none,
                merge=merge,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED:
                raise CollectionUniqueConstraintViolated(e.response, e.request)

            raise e
        else:
            return response

    async def update(
        self,
        document: Union[str, Json],
        return_new: bool = False,
        return_old: bool = False,
        check_for_revisions_match: Optional[bool] = True,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = True,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
        ignore_missing: Optional[bool] = False,
    ) -> Result[Union[bool, Json]]:
        """
        Update a document.

        Parameters
        ----------
        document : str or Json
            Document ID, key or body.
        return_new : bool, default : False
            Include body of the new document in the returned metadata. Ignored if parameter silent is set to True.
        return_old : bool, default : False
            Include body of the old document if overwritten. Ignored if parameter `silent` is set to True. Only available if the `overwrite` option is used.
        check_for_revisions_match : bool, default : True
            If set to `True`, revision of **document** (if given) is compared against the revision of target document.
        keep_none : bool, default : None
            If set to `True`, fields with value None are retained in the document. Otherwise, they are removed completely. Applies only when `overwrite_mode` is set to "update" (update-insert).
        merge : bool, default : None
            If set to True (default), sub-dictionaries are merged instead of the new one overwriting the old one.
        wait_for_sync : bool, default : False
            Wait until the new documents have been synced to disk.
        silent : bool, default : False
            If set to True, no document metadata is returned. This can be used to save resources.
        ignore_missing : bool, default : False
            Do not raise an exception on missing document.

        Returns
        -------
        bool | Json
            Document metadata (e.g. document key, revision), or True if parameter **silent** was set to True, or False if document was not found and
            **ignore_missing** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body.
        aioarango.errors.server.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.server.CollectionUniqueConstraintViolated
            If a unique constraint of the collection is violated.
        aioarango.errors.ArangoServerError
            If update fails.
        """
        try:
            response = await self._documents_api.update_document(
                collection_name=self.name,
                id_prefix=self.id_prefix,
                document=document,
                return_new=return_new,
                return_old=return_old,
                check_for_revisions_match=check_for_revisions_match,
                keep_none=keep_none,
                merge=merge,
                wait_for_sync=wait_for_sync,
                silent=silent,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED:
                raise CollectionUniqueConstraintViolated(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND and ignore_missing:
                return False

            raise e
        else:
            return response

    async def replace(
        self,
        document: Union[str, Json],
        return_new: bool = False,
        return_old: bool = False,
        check_for_revisions_match: Optional[bool] = True,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
        ignore_missing: Optional[bool] = False,
    ) -> Result[Union[bool, Json]]:
        """
        Replace a document.

        Parameters
        ----------
        document : str or Json
            Document ID, key or body.
        return_new : bool, default : False
            Include body of the new document in the returned metadata. Ignored if parameter silent is set to True.
        return_old : bool, default : False
            Include body of the old document if overwritten. Ignored if parameter `silent` is set to True. Only available if the `overwrite` option is used.
        check_for_revisions_match : bool, default : True
            If set to `True`, revision of **document** (if given) is compared against the revision of target document.
        wait_for_sync : bool, default : False
            Wait until the new documents have been synced to disk.
        silent : bool, default : False
            If set to True, no document metadata is returned. This can be used to save resources.
        ignore_missing : bool, default : False
            Do not raise an exception on missing index.


        Returns
        -------
        bool | Json
            Document metadata (e.g. document key, revision), or True if parameter **silent** was set to True, or False if document was not found and
            **ignore_missing** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body.
        aioarango.errors.server.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.server.CollectionUniqueConstraintViolated
            If a unique constraint of the collection is violated.
        aioarango.errors.ArangoServerError
            If replace fails.
        """
        try:
            response = await self._documents_api.replace_document(
                collection_name=self.name,
                id_prefix=self.id_prefix,
                document=document,
                return_new=return_new,
                return_old=return_old,
                check_for_revisions_match=check_for_revisions_match,
                wait_for_sync=wait_for_sync,
                silent=silent,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED:
                raise CollectionUniqueConstraintViolated(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND and ignore_missing:
                return False

            raise e
        else:
            return response

    async def delete(
        self,
        document: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = True,
        return_old: bool = False,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
        ignore_missing: Optional[bool] = False,
    ) -> Result[Union[bool, Json]]:
        """
        Delete a document.

        Parameters
        ----------
        document : str | Json
            Document ID, key or body. Document body must contain the "_id" or "_key" field.
        revision : str, optional
            Expected document revision. Overrides the value of "_rev" field in **document** if present.
        check_for_revisions_match : bool, default : True
            If set to `True`, revision of **document** (if given) is compared against the revision of target document.
        return_old : bool, default : False
            Include body of the old document in the returned metadata. Ignored if parameter **silent** is set to True.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        silent : bool, default : False
            If set to `True`, no document metadata is returned. This can be used to save resources.
        ignore_missing : bool, default : False
            Do not raise an exception on missing index.

        Returns
        -------
        bool | Json
            Document metadata (e.g. document key, revision), or True if parameter **silent** was set to True, or False if document was not found and **ignore_missing** was set to True (does not apply in transactions).

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.server.DocumentRevisionMisMatchError
            If revisions mismatch.
        aioarango.errors.ArangoServerError
            If remove fails.
        """
        try:
            response = await self._documents_api.remove_document(
                collection_name=self.name,
                id_prefix=self.id_prefix,
                document=document,
                revision=revision,
                check_for_revisions_match=check_for_revisions_match,
                return_old=return_old,
                wait_for_sync=wait_for_sync,
                silent=silent,
            )
        except ArangoServerError as e:
            if e.arango_error.type == ErrorType.ARANGO_CONFLICT:
                raise DocumentRevisionMisMatchError(e.response, e.request)

            if e.arango_error.type == ErrorType.ARANGO_DOCUMENT_NOT_FOUND and ignore_missing:
                return False

            raise e
        else:
            return response
