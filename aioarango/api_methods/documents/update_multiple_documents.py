from typing import Union, Optional, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Params, Result
from aioarango.utils.document_utils import ensure_key_in_body, populate_doc_or_error


class UpdateMultipleDocuments(Endpoint):
    error_codes = (
        ErrorType.HTTP_CORRUPTED_JSON,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
    )
    sub_error_codes = (
        ErrorType.HTTP_CORRUPTED_JSON,
        ErrorType.ARANGO_CONFLICT,
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_UNIQUE_CONSTRAINT_VIOLATED,
        ErrorType.ARANGO_DOCUMENT_KEY_BAD,
    )
    status_codes = (
        201,
        # is returned if waitForSync was true and operations were processed.
        202,
        # is returned if waitForSync was false and operations were processed.
        400,  # 600
        # is returned if the body does not contain a valid JSON representation
        # of an array of documents. The response body contains
        # an error document in this case.
        404,  # 1203
        # is returned if the collection specified by collection is unknown.
        # The response body contains an error document in this case.
    )

    async def update_multiple_documents(
        self,
        collection_name: str,
        id_prefix: str,
        documents: List[Json],
        return_new: bool = False,
        return_old: bool = False,
        ignore_revs: Optional[bool] = True,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = True,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """
        Partially updates documents, the documents to update are specified
        by the **_key** attributes in the body objects. The body of the
        request must contain a JSON array of document updates with the
        attributes to patch (the patch documents). All attributes from the
        patch documents will be added to the existing documents if they do
        not yet exist, and overwritten in the existing documents if they do
        exist there.

        Notes
        -----
        - The value of the **_key** attribute as well as attributes used as sharding keys may not be changed.

        - Setting an attribute value to **None** in the patch documents will cause a value of **null** to be saved for the attribute by default.

        - If **ignore_revs** is *false* and there is a **_rev** attribute in a document in the body and its value does not match the revision of the corresponding
          document in the database, the precondition is violated.

        - Cluster only: The patch document may contain
          values for the collection's pre-defined shard keys. Values for the shard keys
          are treated as hints to improve performance. Should the shard keys
          values be incorrect ArangoDB may answer with a not found error

        - Optionally, the query parameter **wait_for_sync** can be used to force
          synchronization of the document replacement operation to disk even in case
          that the **wait_for_sync** flag had been *disabled* for the entire collection.
          Thus, the **wait_for_sync** query parameter can be used to force synchronization
          of just specific operations. To use this, set the **wait_for_sync** parameter
          to *true*. If the **wait_for_sync** parameter is *not specified* or set to
          *false*, then the collection's *default* **wait_for_sync** behavior is
          applied. The **wait_for_sync** query parameter cannot be used to disable
          synchronization for collections that have a default **wait_for_sync** value
          of *true*.

        - The body of the response contains a JSON array of the same length
          as the input array with the information about the identifier and the
          revision of the updated documents. In each entry, the attribute
          **_id** contains the known document-id of each updated document,
          **_key** contains the key which uniquely identifies a document in a
          given collection, and the attribute **_rev** contains the new document
          revision. In case of an error or violated precondition, an error
          object with the attribute error set to *true* and the attribute
          **error_code** set to the error code is built.

        - If the query parameter **return_old** is *true*, then, for each
          generated document, the complete previous revision of the document
          is returned under the **old** attribute in the result.

        - If the query parameter **return_new** is *true*, then, for each
          generated document, the complete new document is returned under
          the **new** attribute in the result.

        - Note that if any precondition is violated or an error occurred with
          some documents, the return code is still `201` or `202`, but
          the additional HTTP header **X-Arango-Error-Codes** is set, which
          contains a map of the error codes that occurred together with their
          multiplicities, as in: `1200:17`,`1205:10` which means that in 17
          cases the error 1200 "revision conflict" and in 10 cases the error
          1205 "illegal document handle" has happened.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
        documents : list of Json
            Document ID, key or body.
        return_new : bool, default : False
            Include body of the new document in the returned metadata. Ignored if parameter silent is set to True.
        return_old : bool, default : False
            Include body of the old document if overwritten. Ignored if parameter `silent` is set to True. Only available if the `overwrite` option is used.
        ignore_revs : bool, default : True
            By `default`, or if this is set to `true`, the `_rev` attributes in
            the given documents are ignored. If this is set to `false`, then
            any `_rev` attribute given in a body document is taken as a
            precondition. The document is only updated if the current revision
            is the one specified.
        keep_none : bool, default : None
            If set to `True`, fields with value None are retained in the document. Otherwise, they are removed completely. Applies only when `overwrite_mode` is set to "update" (update-insert).
        merge : bool, default : None
            If set to True (default), sub-dictionaries are merged instead of the new one overwriting the old one.
        wait_for_sync : bool, default : False
            Wait until the new documents have been synced to disk.
        silent : bool, default : False
            If set to True, no document metadata is returned. This can be used to save resources.
        Returns
        -------
        Result
            Document metadata (e.g. document key, revision) or True if parameter **silent** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.ArangoServerError
            If update fails.
        """
        documents = [ensure_key_in_body(doc, id_prefix) for doc in documents]

        params: Params = {
            "mergeObjects": merge,
            "returnNew": return_new,
            "returnOld": return_old,
            "ignoreRevs": ignore_revs,
            "silent": silent,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync
        if keep_none is not None:
            params["keepNull"] = keep_none

        request = Request(
            method_type=MethodType.PATCH,
            endpoint=f"/_api/document/{collection_name}",
            data=documents,
            params=params,
            write=collection_name,
        )

        def response_handler(response: Response) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            if not response.is_success:
                raise ArangoServerError(response, request)

            if silent:
                return True

            # status_code 201 and 202
            return populate_doc_or_error(
                response,
                request,
                self._connection.prep_bulk_err_response,
            )

        return await self.execute(
            request,
            response_handler,
        )
