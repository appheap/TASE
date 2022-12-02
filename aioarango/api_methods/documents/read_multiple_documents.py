from typing import Union, Sequence, List, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Params, Result
from aioarango.utils.document_utils import ensure_key_in_body, populate_doc_or_error


class ReadMultipleDocuments(Endpoint):
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_DOCUMENT_TYPE_INVALID,
    )
    sub_error_codes = (
        ErrorType.ARANGO_CONFLICT,  # http: 200
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,  # http: 200
        ErrorType.ARANGO_DOCUMENT_HANDLE_BAD,  # http: 200
    )
    status_codes = (
        200,
        400,
        404,  # 1203, 1227
        412,
    )

    async def read_multiple_documents(
        self,
        collection_name: str,
        id_prefix: str,
        documents: Sequence[Union[str, Json]],
        allow_dirty_read: bool = False,
        only_get: Optional[bool] = True,
        ignore_revs: Optional[bool] = True,
    ) -> Result[List[Union[Json, ArangoServerError]]]:
        """
        Returns the documents identified by their **_key** in the body objects. The body of the request must contain a JSON array of either strings (the
        **_key** values to lookup) or search documents.

        Notes
        -----
        - A search document must contain at least a value for the **_key** field.
          A value for **_rev** may be specified to verify whether the document
          has the same revision value, unless **ignoreRevs** is set to `false`.

        - Cluster only: The search document may contain
          values for the collection's pre-defined shard keys. Values for the shard keys
          are treated as hints to improve performance. Should the shard keys
          values be incorrect ArangoDB may answer with a not found error.

        - The returned array of documents contains three special attributes: **_id** containing the document
          identifier, **_key** containing key which uniquely identifies a document
          in a given collection and **_rev** containing the revision.

        Parameters
        ----------
        collection_name : str
            Collection name.
        id_prefix : str
            ID prefix for this document.
        documents : sequence of str or Json
            List of document keys, IDs or bodies. Document bodies must contain the "_id" or "_key" fields.
        allow_dirty_read : bool, default : False
            Whether to allow reads from followers in a cluster.
        ignore_revs : bool, default : True
            Should the value be true (the default): If a search document contains a value for the "_rev" field, then the document is only returned if it has
            the same revision value. Otherwise, a precondition failed error is returned.
        only_get : bool, default : True
            This parameter is required to be "true", otherwise a replace operation is executed!.

        Returns
        -------
        Result
            Documents. Missing ones are not included.

        Raises
        ------
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.ArangoServerError
            If retrieval fails.
        """
        documents = [ensure_key_in_body(doc, id_prefix) if isinstance(doc, dict) else doc for doc in documents]
        params: Params = {
            "onlyget": only_get,
            "ignoreRevs": "true" if ignore_revs else "false",
        }

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/document/{collection_name}",
            params=params,
            data=documents,
            read=collection_name,
            headers={"x-arango-allow-dirty-read": "true"} if allow_dirty_read else None,
        )

        def response_handler(response: Response) -> List[Union[Json, ArangoServerError]]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200 :  if no error happened
            return populate_doc_or_error(
                response,
                request,
                self._connection.prep_bulk_err_response,
            )

        return await self.execute(
            request,
            response_handler,
        )
