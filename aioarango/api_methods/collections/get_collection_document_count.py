from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, ArangoCollection
from aioarango.typings import Result


class GetCollectionDocumentCount(Endpoint):
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def get_collection_document_count(
        self,
        name: str,
    ) -> Result[ArangoCollection]:
        """
        Get number of documents in a collection.

        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            An `ArangoCollection` object. (full version with `count` attribute)

        Raises
        ------
        ValueError
            If name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/collection/{name}/count",
            read=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
