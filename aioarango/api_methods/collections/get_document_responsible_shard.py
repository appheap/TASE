from typing import Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Json, Result
from aioarango.utils.document_utils import ensure_key_in_body


class GetDocumentResponsibleShard:
    error_codes = (
        ErrorType.ARANGO_DOCUMENT_NOT_FOUND,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.CLUSTER_ONLY_ON_COORDINATOR,
    )
    status_codes = (
        200,
        # Returns the ID of the responsible shard.
        400,
        # If the collection-name is missing, then a HTTP 400 is
        # returned.
        # Additionally, if not all of the collection's shard key
        # attributes are present in the input document, then a
        # HTTP 400 is returned as well.
        404,  # 1202, 1203
        # If the collection-name is unknown, then an HTTP 404 is returned.
        501,  # 1471
        # HTTP 501 is returned if the method is called on a single server.
    )

    async def get_document_responsible_shard(
        self: Endpoint,
        name: str,
        document: Union[str, Json],
        id_prefix: str,
    ) -> Result[str]:
        """
        Return the ID of the shard that is responsible for the given document
        (if the document exists) or that would be responsible if such document
        existed.

        Notes
        -----
        - **Important**: This method is only available in a `cluster Coordinator`.
        - The request must body must contain a JSON document with at least the collection's shard key attributes set to some values.
        - The response is a JSON object with a **shardId** attribute, which will contain the ID of the responsible shard.



        Parameters
        ----------
        name : str
            Name of the collection.
        document : str or Json
            Document ID, key or body.
        id_prefix : str
            ID prefix for the document.

        Returns
        -------
        Result
            Responsible Shard ID for the document.

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.DocumentParseError
            If `key` and `ID` are missing from the document body, or if collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        document = ensure_key_in_body(document, id_prefix)

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/responsibleShard",
            data=document
            if isinstance(document, dict)
            else {
                "_key": document,
            },
        )

        def response_handler(response: Response) -> str:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body["shardId"]

        return await self.execute(request, response_handler)
