from typing import Union, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType, OverwriteMode
from aioarango.errors import CollectionNotFoundError, DocumentIllegalError, DocumentUniqueConstraintError, DocumentInsertError
from aioarango.models import Request, Response
from aioarango.typings import Json, Params
from aioarango.utils.document_utils import ensure_key_from_id


class CreateDocument:
    async def create_document(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        document: Union[str, Json],
        return_new: bool = False,
        sync: Optional[bool] = None,
        silent: bool = False,
        overwrite: bool = False,
        return_old: bool = False,
        overwrite_mode: Optional[OverwriteMode] = None,
        keep_none: Optional[bool] = None,
        merge: Optional[bool] = None,
    ) -> Union[bool, Json]:
        """
        Creates a new document from the document given in the body, unless there is already a document with the **_key** given. If no **_key** is given,
        a new unique **_key** is generated automatically.

        Notes
        -----
        - Possibly given **_id** and **_rev** attributes in the body are always ignored, the URL part or the query parameter collection respectively counts.

        - If the document was created successfully, then the **Location** header contains the path to the newly created document. The **Etag** header field
          contains the revision of the document. Both are only set in the single document case.

        - If silent is not set to true, the body of the response contains a JSON object with the following attributes:

          - **_id** contains the document identifier of the newly created document
          - **_key** contains the document key
          - **_rev** contains the document revision

        - If the collection parameter **waitForSync** is `false`, then the call returns as soon as the document has been accepted. It will not wait until the
          documents have been synced to disk.

        - Optionally, the query parameter **waitForSync** can be used to force synchronization of the document creation operation to disk even in
          case that the **waitForSync** flag had been disabled for the entire collection. Thus, the **waitForSync** query parameter can be used to
          force synchronization of just this specific operations. To use this, set the **waitForSync** parameter to `true`. If the **waitForSync**
          parameter is `not specified` or set to `false`, then the collection's default **waitForSync** behavior is applied. The **waitForSync** query
          parameter cannot be used to disable synchronization for collections that have a `default` **waitForSync** value of `true`.

        - If the query parameter **returnNew** is `true`, then, for each generated document, the complete new document is returned under the **new**
          attribute in the result.

        - When using **keep_none** parameter, If the intention is to delete existing attributes with the `update-insert` command, the URL query parameter **keepNull** can be used with a value of
          `false`. This will modify the behavior of the patch command to remove any attributes from the existing document that are contained in the patch document
          with an attribute value of null. This option controls the update-insert behavior only.

        - The **merge** controls whether objects (not arrays) will be merged if present in both the existing and the `update-insert` document. If set to
          `false`, the value in the patch document will overwrite the existing document's value. If set to `true`, objects will be merged. *The default is
          true*. This option controls the `update-insert` behavior only.


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
        sync :
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
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.DocumentIllegalError
            If document format is illegal.
        aioarango.errors.DocumentUniqueConstraintError
            If document violates a unique constraint.
        aioarango.errors.DocumentInsertError
            If insert fails.
        """
        document = ensure_key_from_id(document, id_prefix)

        params: Params = {
            "returnNew": return_new,
            "silent": silent,
            "overwrite": overwrite,
            "returnOld": return_old,
        }
        if sync is not None:
            params["waitForSync"] = sync
        if overwrite_mode is not None:
            params["overwriteMode"] = str(overwrite_mode.value)
        if keep_none is not None:
            params["keepNull"] = keep_none
        if merge is not None:
            params["mergeObjects"] = merge

        request = Request(
            method_type=MethodType.POST,
            endpoint=f"/_api/document/{collection_name}",
            data=document,
            params=params,
            write=collection_name,
        )

        def response_handler(response: Response) -> Union[bool, Json]:
            if response.error_code == 1203:  # collection or view not found (status_code 404)
                raise CollectionNotFoundError(response, request)

            if response.error_code == 600:  # document format is illegal (status_code 400)
                # the body does not contain a valid JSON representation of one document.
                raise DocumentIllegalError(response, request)

            if response.error_code == 1210:  # status_code 409
                raise DocumentUniqueConstraintError(response, request)

            if not response.is_success:
                raise DocumentInsertError(response, request)

            # status_code 201 and 202
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
