from typing import Union, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import (
    CollectionNotFoundError,
    DocumentIllegalError,
    DocumentIllegalKeyError,
    DocumentUpdateError,
    DocumentRevisionMisMatchError,
    DocumentUniqueConstraintError,
    DocumentReplaceError,
)
from aioarango.models import Request, Response
from aioarango.typings import Json, Params, Result
from aioarango.utils.document_utils import prep_from_doc


class ReplaceDocument:
    async def replace_document(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        document: Union[str, Json],
        return_new: bool = False,
        return_old: bool = False,
        check_for_revisions_match: Optional[bool] = True,
        wait_for_sync: Optional[bool] = None,
        silent: bool = False,
    ) -> Result[Union[bool, Json]]:
        """
        Replaces the specified document with the one in the body, provided there is such a document and no precondition is violated.

        Notes
        -----
        - The value of the **_key** attribute as well as attributes used as sharding keys may not be changed.

        - If the **If-Match** header is specified and the revision of the
          document in the database is unequal to the given revision, the precondition is violated.

        - If **If-Match** is not given and **ignoreRevs** is *false* and there
          is a *_rev* attribute in the body and its value does not match
          the revision of the document in the database, the precondition is
          violated.

        - If a precondition is violated, an HTTP *412* is returned.

        - If the document exists and can be updated, then an HTTP *201* or
          an HTTP *202* is returned (depending on **wait_for_sync**, see below),
          the **Etag** header field contains the new revision of the document
          (in double quotes) and the **Location** header contains a complete URL
          under which the document can be queried.

        - Cluster only: The replacing documents may contain
          values for the collection's pre-defined shard keys. Values for the shard keys
          are treated as hints to improve performance. Should the shard keys
          values be incorrect ArangoDB may answer with a `not found error`.

        - Optionally, the query parameter **wait_for_sync** can be used to force
          synchronization of the updated document operation to disk even in case
          that the **wait_for_sync** flag had been *disabled* for the entire collection.
          Thus, the **wait_for_sync** query parameter can be used to force synchronization
          of just specific operations. To use this, set the **wait_for_sync** parameter
          to *true*. If the **wait_for_sync** parameter is *not specified* or set to
          *false*, then the collection's *default* **wait_for_sync** behavior is
          applied. The **wait_for_sync** query parameter cannot be used to disable
          synchronization for collections that have a default **wait_for_sync** value
          of *true*.

        - If **silent** is not set to *true*, the body of the response contains a JSON
          object with the information about the identifier and the revision. The attribute
          **_id** contains the known document-id of the updated document, **_key**
          contains the key which uniquely identifies a document in a given collection,
          and the attribute **_rev** contains the new document revision.

        - If the query parameter **return_old** is *true*, then, for each
          generated document, the complete previous revision of the document
          is returned under the **old** attribute in the result.

        - If the query parameter **return_new** is *true*, then, for each
          generated document, the complete new document is returned under
          the **new** attribute in the result.

        - If the document does not exist, then a HTTP `404` is returned and the
          body of the response contains an error document.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
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
        Returns
        -------
        Result
            Document metadata (e.g. document key, revision) or True if parameter **silent** was set to True.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.DocumentIllegalError
            If document format is illegal.
        aioarango.errors.DocumentIllegalKeyError
            If document key is illegal.
        aioarango.errors.DocumentUniqueConstraintError
            If document violates a unique constraint.
        aioarango.errors.DocumentRevisionMisMatchError
            If the given document revision does not match with the one in the database.
        aioarango.errors.DocumentReplaceError
            If replace fails.
        """

        handle, body, headers = prep_from_doc(
            document,
            id_prefix,
            check_for_revisions_match=check_for_revisions_match,
        )

        params: Params = {
            "returnNew": return_new,
            "returnOld": return_old,
            "ignoreRevs": not check_for_revisions_match,
            #  (ignoreRevs):  By `default`, or if this is set to `true`, the `_rev` attributes in
            # the given documents are ignored. If this is set to `false`, then
            # any `_rev` attribute given in a body document is taken as a
            # precondition. The document is only updated if the current revision
            # is the one specified.
            "silent": silent,
        }
        if wait_for_sync is not None:
            params["waitForSync"] = wait_for_sync

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/document/{handle}",
            data=document,
            params=params,
            headers=headers,
            write=collection_name,
        )

        def response_handler(response: Response) -> Union[bool, Json]:
            if response.status_code == 404:
                if response.error_code == 1203:  # collection or view not found (status_code 404)
                    raise CollectionNotFoundError(response, request)
                else:
                    # This must not happen
                    raise DocumentReplaceError(response, request)

            elif response.status_code == 400:
                # if the body does not contain a valid JSON representation of one document. The response body contains an error document in this case.
                if response.error_code == 600:  # document format is illegal (status_code 400)
                    # the body does not contain a valid JSON representation of one document.
                    raise DocumentIllegalError(response, request)
                elif response.error_code == 1221:  # illegal document key
                    raise DocumentIllegalKeyError(response, request)
                else:
                    # This must not happen
                    raise DocumentReplaceError(response, request)

            elif response.status_code == 409:
                # In the single document case if a document with the
                # same qualifiers in an indexed attribute conflicts with an already
                # existing document and thus violates that unique constraint. The
                # response body contains an error document in this case.
                if response.error_code == 1210:  # status_code 409
                    raise DocumentUniqueConstraintError(response, request)
                else:
                    # This must not happen
                    raise DocumentReplaceError(response, request)

            elif response.status_code == 412:
                # if the precondition was violated. The response will
                # also contain the found documents' current revisions in the `_rev`
                # attributes. Additionally, the attributes `_id` and `_key` will be returned.
                if response.error_code == 1200:
                    raise DocumentRevisionMisMatchError(response, request)
                else:
                    # This must not happen
                    raise DocumentUpdateError(response, request)

            if not response.is_success:
                raise DocumentReplaceError(response, request)

            # status_code 200, 201 and 202
            # 201 : The documents were created successfully and waitForSync was true.
            # 202 : The documents were created successfully and waitForSync was false.

            if silent:
                return True

            result: Json = response.body
            if "_oldRev" in result:
                result["_old_rev"] = result.pop("_oldRev")
            return result

        return await self.execute(
            request,
            response_handler,
        )
