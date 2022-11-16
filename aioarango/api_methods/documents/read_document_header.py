from typing import Union, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import CollectionNotFoundError, DocumentRevisionMisMatchError, DocumentGetError, DocumentRevisionMatchError
from aioarango.models import Request, Response
from aioarango.typings import Json, Headers, Result
from aioarango.utils.document_utils import prep_from_doc


class ReadDocumentHeader:
    async def read_document_header(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        document: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        check_for_revisions_mismatch: Optional[bool] = None,
        allow_dirty_read: bool = False,
    ) -> Result[Optional[Headers]]:
        """
        Return the document header identified by `document-id`. Only returns the header fields and not the body. You can use this call to get the current
        revision of a document or check if the document was deleted.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
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
        Result
            Document, or None if not found.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.client.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.DocumentRevisionMatchError
            If given revision matches the document revision in the database (document has not been updated).
        aioarango.errors.client.DocumentRevisionMisMatchError
            if given revision does not match the document revision in the database (document has been updated).
        aioarango.errors.DocumentGetError
            If retrieval fails.
        """
        handle, body, headers = prep_from_doc(
            document,
            id_prefix,
            revision,
            check_for_revisions_match=check_for_revisions_match,
            check_for_revisions_mismatch=check_for_revisions_mismatch,
        )

        request = Request(
            method_type=MethodType.HEAD,
            endpoint=f"/_api/document/{handle}",
            headers=headers,
            read=collection_name,
        )

        if allow_dirty_read:
            headers["x-arango-allow-dirty-read"] = "true"

        def response_handler(response: Response) -> Optional[Headers]:
            if response.status_code == 404:  # if the document or collection was not found
                # todo: `error_code` is None, so none of the following checks will happen except the `else` clause
                if response.error_code == 1202:  # document not found (status_code 404)
                    return None
                elif response.error_code == 1203:  # collection or view not found (status_code 404)
                    raise CollectionNotFoundError(response, request)
                else:
                    return None

            elif response.status_code == 304:  # the document in the db has not been updated
                raise DocumentRevisionMatchError(response, request)

            elif response.status_code == 412:  # the document in the db has been updated
                raise DocumentRevisionMisMatchError(response, request)

            if not response.is_success:
                raise DocumentGetError(response, request)

            # status_code 200 : if the document was found
            return response.headers

        return await self.execute(
            request,
            response_handler,
        )
