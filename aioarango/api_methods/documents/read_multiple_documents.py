from typing import Union, Sequence, List, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import CollectionNotFoundError, DocumentGetError, DocumentIllegalError, DocumentRevisionMisMatchError
from aioarango.models import Request, Response
from aioarango.typings import Json, Params, Result
from aioarango.utils.document_utils import extract_id


class ReadMultipleDocuments:
    async def read_multiple_documents(
        self: Endpoint,
        collection_name: str,
        id_prefix: str,
        documents: Sequence[Union[str, Json]],
        allow_dirty_read: bool = False,
        only_get: Optional[bool] = True,
        ignore_revs: Optional[bool] = True,
    ) -> Result[List[Json]]:
        """
        Returns the documents identified by their **_key** in the body objects. The body of the request must contain a JSON array of either strings (the
        **_key** values to lookup) or search documents.

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
        aioarango.errors.CollectionNotFoundError
            If collection with the given name does not exist in the database.
        aioarango.errors.DocumentIllegalError
            If document format is illegal.
        aioarango.errors.DocumentRevisionMisMatchError
            if given revision does not match the document revision in the database (document has been updated).
        aioarango.errors.DocumentGetError
            If retrieval fails.
        """
        handles = [extract_id(d, id_prefix) if isinstance(d, dict) else d for d in documents]
        params: Params = {
            "onlyget": only_get,
            "ignoreRevs": "true" if ignore_revs else "false",
        }

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/document/{collection_name}",
            params=params,
            data=handles,
            read=collection_name,
            headers={"x-arango-allow-dirty-read": "true"} if allow_dirty_read else None,
        )

        def response_handler(response: Response) -> List[Json]:
            if response.error_code == 1203:  # collection or view not found (status_code 404)
                raise CollectionNotFoundError(response, request)

            if response.status_code == 400:
                # is returned if the body does not contain a valid JSON representation
                # of an array of documents. The response body contains
                # an error document in this case.
                raise DocumentIllegalError(response, request)  # this should not happen, since the `keys` are extracted from the given documents

            if response.status_code == 412:  # the document in the db has been updated
                # todo: check if this happens
                # this should not happen, since the `keys` are extracted from the given documents
                raise DocumentRevisionMisMatchError(response, request)

            if not response.is_success:
                raise DocumentGetError(response, request)

            # status_code 200 :  if no error happened
            return [doc for doc in response.body if "_id" in doc]

        return await self.execute(
            request,
            response_handler,
        )
