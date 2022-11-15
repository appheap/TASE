from typing import Union, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors.server.collection_errors import CollectionNotFoundError
from aioarango.errors.server.document_errors import DocumentRevisionMisMatchError, DocumentGetError, DocumentRevisionMatchError
from aioarango.models import Request, Response
from aioarango.typings import Json
from aioarango.utils.document_utils import prep_from_doc


class ReadDocument:
    async def read_document(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        document: Union[str, Json],
        rev: Optional[str] = None,
        revisions_must_match: Optional[bool] = None,
        allow_dirty_read: bool = False,
    ) -> Optional[Json]:
        """
        Return the document identified by `document-id`. The returned document contains three special attributes: `_id` containing the document identifier,
        `_key` containing key which uniquely identifies a document in a given collection and `_rev` containing the revision.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
        document : str or Json
            Document ID, key or body.
        rev : str, default : None
            Document revision to check. Overrides the value of "_rev" field in `document` if present.
        revisions_must_match : bool, default : None
            Whether the given revision and the document revision in the database must match or not.
        allow_dirty_read : bool, default : False
            Whether to allow reads from followers in a cluster.

        Returns
        -------
        Json, optional
            Document, or None if not found.

        Raises
        ------
        aioarango.errors.client.document_errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.client.document_errors.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.client.document_errors.DocumentRevisionMatchError
            If given revision matches the document revision in the database (document has not been updated).
        aioarango.errors.client.document_errors.DocumentRevisionMisMatchError
            if given revision does not match the document revision in the database (document has been updated).
        aioarango.errors.client.document_errors.DocumentGetError
            If retrieval fails.
        """
        handle, body, headers = prep_from_doc(
            document,
            id_prefix,
            rev,
            revisions_must_match,
        )

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/document/{handle}",
            headers=headers,
            read=collection_name,
        )

        if allow_dirty_read:
            headers["x-arango-allow-dirty-read"] = "true"

        def response_handler(response: Response) -> Optional[Json]:
            if response.error_code == 1202:  # document not found
                return None

            if response.error_code == 1203:  # collection or view not found
                raise CollectionNotFoundError(response, request)

            if response.status_code == 304:  # the document in the db has not been updated
                raise DocumentRevisionMatchError(response, request)

            if response.status_code == 412:  # the document in the db has been updated
                raise DocumentRevisionMisMatchError(response, request)

            if not response.is_success:
                raise DocumentGetError(response, request)

            return response.body

        return await self.execute(
            request,
            response_handler,
        )
