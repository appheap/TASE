from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Response, Request
from aioarango.typings import Result


class RecalculateCollectionDocumentCount:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        # If the document count was recalculated successfully, HTTP 200 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def recalculate_collection_document_count(
        self: Endpoint,
        name: str,
    ) -> Result[bool]:
        """
        Recalculate the document count of a collection, if it ever becomes inconsistent.

        Notes
        -----
        It returns an object with the attributes:
            - **result**: will be true if recalculating the document count succeeded.


        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            `True` if the operation was successful.

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/recalculateCount",
            read=name,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body["result"]

        return await self.execute(request, response_handler)
