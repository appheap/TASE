import collections
from typing import Union, List, Sequence, Optional, Deque

from aioarango.api import Endpoint
from aioarango.enums import MethodType, OverwriteMode
from aioarango.errors import (
    DocumentInsertError,
    DocumentRevisionMisMatchError,
    DocumentIllegalKeyError,
    DocumentNotFoundError,
    DocumentIllegalError,
    DocumentUniqueConstraintError,
)
from aioarango.errors.base import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Json, Result, Params
from aioarango.utils.document_utils import ensure_key_from_id


class CreateMultipleDocuments:
    async def create_multiple_documents(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        documents: Sequence[Json],
        return_new: bool = False,
        return_old: bool = False,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
        overwrite: bool = False,
        overwrite_mode: Optional[OverwriteMode] = None,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = None,
    ) -> Result[Union[bool, List[Union[Json, ArangoServerError]]]]:
        """
        Creates new documents from the documents given in the body, unless there
        is already a document with the **_key** given. If no **_key** is given, a new
        unique **_key** is generated automatically.

        Notes
        -----
        - The result body will contain a JSON array of the
          same length as the input array, and each entry contains the result
          of the operation for the corresponding input. In case of an error
          the entry is a document with attributes error set to `true` and
          **error_code** set to the error code that has happened.

        - Possibly given **_id** and **_rev** attributes in the body are always ignored,
          the URL part or the query parameter collection respectively counts.

        - If silent is not set to `true`, the body of the response contains an
          array of JSON objects with the following attributes:

          - **_id** contains the document identifier of the newly created document
          - **_key** contains the document key
          - **_rev** contains the document revision

        - If the collection parameter **wait_for_sync** is `false`, then the call
          returns as soon as the documents have been accepted. It will not wait
          until the documents have been synced to disk.

        - Optionally, the query parameter **wait_for_sync** can be used to force
          synchronization of the document creation operation to disk even in
          case that the **wait_for_sync** flag had been disabled for the entire
          collection. Thus, the **wait_for_sync** query parameter can be used to
          force synchronization of just this specific operations. To use this,
          set the **wait_for_sync** parameter to `true`. If the **wait_for_sync**
          parameter is not specified or set to `false`, then the collection's
          default **wait_for_sync** behavior is applied. The **wait_for_sync** query
          parameter cannot be used to disable synchronization for collections
          that have a default **wait_for_sync** value of `true`.

        - If the query parameter **return_new** is `true`, then, for each
          generated document, the complete new document is returned under
          the **new** attribute in the result.

        - Should an error have occurred with some documents
          the additional HTTP header **X-Arango-Error-Codes** is set, which
          contains a map of the error codes that occurred together with their
          multiplicities, as in: `1205:10`, `1210:17` which means that in 10
          cases the error 1205 "illegal document handle" and in 17 cases the
          error 1210 "unique constraint violated" has happened.



        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
        documents : list of Json
            List of new documents to insert. If they contain the
            `_key` or `_id` fields, the values are used as the keys of the new
            documents (auto-generated otherwise). Any `_rev` field is ignored.
        return_new : bool, default : False
            Include bodies of the new documents in the returned
            metadata. Ignored if parameter **silent** is set to `True`.
        return_old : bool, default : False
            Include body of the old documents if replaced. Applies only when value of **overwrite** is set to True.
        wait_for_sync : bool, optional
            Block until operation is synchronized to disk.
        silent : bool, default : False
            If set to `True`, no document metadata is returned. This can be used to save resources.
        overwrite : bool, default : False
            If set to `True`, operation does not fail on duplicate keys and the existing documents are replaced.
        overwrite_mode : OverwriteMode, optional
            Overwrite behavior used when the document key exists already. Implicitly sets the value of parameter `overwrite`.
        keep_none : bool, optional
            If set to `True`, fields with value `None` are retained
            in the document. Otherwise, they are removed completely. Applies
            only when **overwrite_mode** is set to "update" (update-insert).
        merge : bool, optional
            If set to `True` (default), sub-dictionaries are merged
            instead of the new one overwriting the old one. Applies only when
            **overwrite_mode** is set to "update" (update-insert).

        Returns
        -------
        Result
            List of document metadata (e.g. document keys, revisions) and
            any exception, or `True` if parameter **silent** was set to `True`.

        """
        documents = [ensure_key_from_id(doc, id_prefix) for doc in documents]

        params: Params = {
            "returnNew": return_new,
            "silent": silent,
            "overwrite": overwrite,
            "returnOld": return_old,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync
        if overwrite_mode is not None:
            params["overwriteMode"] = str(overwrite_mode.value)
        if keep_none is not None:
            params["keepNull"] = keep_none
        if merge is not None:
            params["mergeObjects"] = merge

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/document/{collection_name}",
            data=documents,
            params=params,
        )

        def response_handler(
            response: Response,
        ) -> Union[bool, List[Union[Json, ArangoServerError]]]:
            if not response.is_success:
                raise DocumentInsertError(response, request)
            if silent is True:
                return True

            results: Deque[Union[Json, ArangoServerError]] = collections.deque()
            for body in response.body:
                if "_id" in body:
                    if "_oldRev" in body:
                        body["_old_rev"] = body.pop("_oldRev")
                    results.append(body)
                else:
                    sub_resp = self.connection.prep_bulk_err_response(response, body)

                    error: ArangoServerError
                    if sub_resp.error_code == 600:  # document format is illegal (status_code 400)
                        # the body does not contain a valid JSON representation of one document.
                        error = DocumentIllegalError(sub_resp, request)
                    elif sub_resp.error_code == 1202:  # document not found
                        error = DocumentNotFoundError(sub_resp, request)
                    elif sub_resp.error_code == 1221:  # illegal document key
                        error = DocumentIllegalKeyError(sub_resp, request)
                    elif sub_resp.error_code == 1210:  # status_code 409
                        error = DocumentUniqueConstraintError(response, request)
                    elif sub_resp.error_code == 1200:
                        error = DocumentRevisionMisMatchError(sub_resp, request)
                    else:
                        # This must not happen
                        error = DocumentInsertError(sub_resp, request)

                    results.append(error)

            # status_code 201 and 202
            # 201 : if waitForSync was true and operations were processed.
            # 202 : if waitForSync was false and operations were processed.
            return list(results)

        return await self.execute(request, response_handler)
