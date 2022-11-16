from typing import Union, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import CollectionNotFoundError, DocumentRevisionMisMatchError, DocumentGetError, DocumentRevisionMatchError
from aioarango.models import Request, Response
from aioarango.typings import Json, Result
from aioarango.utils.document_utils import prep_from_doc


class ReadDocument:
    async def read_document(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        document: Union[str, Json],
        rev: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = None,
        allow_dirty_read: bool = False,
    ) -> Result[Optional[Json]]:
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
        check_for_revisions_match : bool, default : None
            Whether the given revision and the document revision in the database must match or not.
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
        aioarango.errors.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.DocumentRevisionMatchError
            If given revision matches the document revision in the database (document has not been updated).
        aioarango.errors.DocumentRevisionMisMatchError
            if given revision does not match the document revision in the database (document has been updated).
        aioarango.errors.DocumentGetError
            If retrieval fails.
        """
        handle, body, headers = prep_from_doc(
            document,
            id_prefix,
            rev,
            check_for_revisions_match=check_for_revisions_match,
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
            if response.status_code == 404:  # if the document or collection was not found
                if response.error_code == 1202:  # document not found (status_code 404)
                    return None
                elif response.error_code == 1203:  # collection or view not found (status_code 404)
                    raise CollectionNotFoundError(response, request)
                else:
                    # This must not happen
                    raise DocumentGetError(response, request)

            elif response.status_code == 304:  # the document in the db has not been updated
                raise DocumentRevisionMatchError(response, request)

            elif response.status_code == 412:  # the document in the db has been updated
                if response.error_code == 1200:
                    raise DocumentRevisionMisMatchError(response, request)
                else:
                    # This must not happen
                    raise DocumentGetError(response, request)

            if not response.is_success:
                raise DocumentGetError(response, request)

            # status_code 200 : if the document was found
            return response.body

        return await self.execute(
            request,
            response_handler,
        )
