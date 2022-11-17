from typing import Optional, Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Params, Result
from aioarango.utils.document_utils import prep_from_doc


class RemoveDocument:
    error_codes = (
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_CONFLICT,
    )
    status_codes = (
        200,
        # is returned if the document was removed successfully and waitForSync was true.
        202,
        # is returned if the document was removed successfully and waitForSync was false.
        404,  # 1202, 1203
        # is returned if the collection or the document was not found. The response body contains an error document in this case.
        412,  # 1200
        # is returned if a "If-Match" header or rev is given and the found
        # document has a different version. The response will also contain the found
        # document's current revision in the _rev attribute. Additionally, the
        # attributes _id and _key will be returned.
    )

    async def remove_document(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        document: Union[str, Json],
        revision: Optional[str] = None,
        check_for_revisions_match: Optional[bool] = True,
        return_old: bool = False,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """
        Removes a document.


        Notes
        -----
        - If silent is not set to `true`, the body of the response contains a JSON
          object with the information about the identifier and the revision. The attribute
          **_id** contains the known document-id of the removed document, **_key**
          contains the key which uniquely identifies a document in a given collection,
          and the attribute **_rev** contains the document revision.

        - If the **wait_for_sync** parameter is not specified or set to `false`,
          then the collection's default **wait_for_sync** behavior is applied.
          The **wait_for_sync** query parameter cannot be used to disable
          synchronization for collections that have a default **wait_for_sync**
          value of `true`.

        - If the query parameter **return_old** is `true`, then
          the complete previous revision of the document is returned under the old attribute in the result.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
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

        Returns
        -------
        Result
            Document metadata (e.g. document key, revision), or True if parameter **silent** was set to True, or False if document was not found and **ignore_missing** was set to True (does not apply in transactions).


        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.ArangoServerError
            If remove fails.
        """
        handle, body, headers = prep_from_doc(
            document,
            id_prefix,
            revision,
            check_for_revisions_match=check_for_revisions_match,
        )

        params: Params = {
            "returnOld": return_old,
            "ignoreRevs": not check_for_revisions_match,
            "silent": silent,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/document/{handle}",
            params=params,
            headers=headers,
            write=collection_name,
        )

        def response_handler(response: Response) -> Union[bool, Json]:
            if response.status_code in (404, 412) or not response.is_success:
                raise ArangoServerError(response, request)

            # status code 200 and 202:
            return True if silent else response.body

        return await self.execute(request, response_handler)
