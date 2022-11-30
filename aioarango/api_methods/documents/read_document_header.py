from typing import Union, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Json, Headers, Result
from aioarango.utils.document_utils import prep_from_doc


class ReadDocumentHeader(Endpoint):
    error_types = (
        # this endpoint does not return any `error_code`
    )

    status_codes = (
        200,
        # is returned if the document was found.
        304,  # `error_code` is `None`.
        # is returned if the "If-None-Match" header is given and the document has the same version.
        404,  # `error_code` is `None`.
        # is returned if the document or collection was not found.
        412,  # `error_code` is `None`.
        # is returned if an "If-Match" header is given and the found
        # document has a different version. The response will also contain the found
        # document's current revision in the Etag header.
    )

    async def read_document_header(
        self,
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
        aioarango.errors.ArangoServerError
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
            # the `error_code` attribute of the `response` object is `None`, only `status_code` is available for this endpoint
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200 : if the document was found
            return response.headers

        return await self.execute(
            request,
            response_handler,
        )
