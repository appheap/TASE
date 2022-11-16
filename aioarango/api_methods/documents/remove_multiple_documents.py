import collections
from typing import Optional, Sequence, Union, List, Deque

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Json, Result, Params
from aioarango.utils.document_utils import ensure_key_in_body


class RemoveMultipleDocuments:
    async def remove_multiple_documents(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        documents: Sequence[Union[str, Json]],
        return_old: bool = False,
        check_for_revisions_match: bool = True,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """
        Removes multiple documents.


        Notes
        -----
        - The body of the request is an array consisting of selectors for
          documents. A selector can either be a string with a key or a string
          with a document identifier or an object with a **_key** attribute. This
          API call removes all specified documents from collection.
          If the **ignoreRevs** query parameter is `false` and the
          selector is an object and has a **_rev** attribute, it is a
          precondition that the actual revision of the removed document in the
          collection is the specified one.

        - The body of the response is an array of the same length as the input
          array. For each input selector, the output contains a JSON object
          with the information about the outcome of the operation. If no error
          occurred, an object is built in which the attribute **_id** contains
          the known document-id of the removed document, **_key** contains
          the key which uniquely identifies a document in a given collection,
          and the attribute **_rev** contains the document revision. In case of
          an error, an object with the attribute error set to `true` and
          **error_code** set to the error code is built.

        - If the **wait_for_sync** parameter is not specified or set to `false`,
          then the collection's default **wait_for_sync** behavior is applied.
          The **wait_for_sync** query parameter cannot be used to disable
          synchronization for collections that have a default **wait_for_sync**
          value of `true`.

        - If the query parameter **return_old** is `true`, then
          the complete previous revision of the document
          is returned under the **old** attribute in the result.

        - Note that if any precondition is violated or an error occurred with
          some documents, the return code is still `200` or `202`, but
          the additional HTTP header **X-Arango-Error-Codes** is set, which
          contains a map of the error codes that occurred together with their
          multiplicities, as in: `1200:17`,`1205:10` which means that in `17`
          cases the error `1200` "revision conflict" and in `10` cases the error
          `1205` "illegal document handle" has happened.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
        documents : list
            Document IDs, keys or bodies. Document bodies must contain the "_id" or "_key" fields.
        return_old : bool, default : False
            Include bodies of the old documents in the result.
        check_for_revisions_match : bool, default : True
            If set to `True`, revision of **document** (if given) is compared against the revision of target document.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        silent : bool, default : False
            If set to `True`, no document metadata is returned. This can be used to save resources.

        Returns
        -------
        Result
            List of document metadata (e.g. document keys, revisions) and
            any exceptions, or `True` if parameter **silent** was set to `True`.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.DocumentNotFoundError
            If document was not found in the collection.
        aioarango.errors.DocumentIllegalError
            If document format is illegal.
        aioarango.errors.DocumentIllegalKeyError
            If document key is illegal.
        aioarango.errors.DocumentRevisionMisMatchError
            If the given document revision does not match with the one in the database.
        aioarango.errors.DocumentDeleteError
            If remove fails.
        """
        params: Params = {
            "returnOld": return_old,
            "ignoreRevs": not check_for_revisions_match,
            "silent": silent,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        documents = [ensure_key_in_body(doc, id_prefix) if isinstance(doc, dict) else doc for doc in documents]

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/document/{collection_name}",
            params=params,
            data=documents,
            write=collection_name,
        )

        def response_handler(
            resp: Response,
        ) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not resp.is_success:
                raise ArangoServerError(resp, request)

            if silent is True:
                return True

            results: Deque[Union[Json, ArangoServerError]] = collections.deque()
            for body in resp.body:
                if "_id" in body:
                    results.append(body)
                else:
                    sub_resp = self.connection.prep_bulk_err_response(resp, body)

                    error: ArangoServerError
                    if sub_resp.error_code == 600:  # document format is illegal (status_code 400)
                        # the body does not contain a valid JSON representation of one document.
                        error = ArangoServerError(sub_resp, request)
                    elif sub_resp.error_code == 1202:  # document not found
                        error = ArangoServerError(sub_resp, request)
                    elif sub_resp.error_code == 1221:  # illegal document key
                        error = ArangoServerError(sub_resp, request)
                    elif sub_resp.error_code == 1200:
                        error = ArangoServerError(sub_resp, request)
                    else:
                        # This must not happen
                        error = ArangoServerError(sub_resp, request)

                    results.append(error)

            # status_code 200 and 202
            # 200 : if waitForSync was true.
            # 202 : if waitForSync was false.
            return list(results)

        return await self.execute(request, response_handler)
