from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, ArangoCollection
from aioarango.typings import Result


class ReadCollectionInfo:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
        200,
    )

    async def read_collection_info(
        self: Endpoint,
        name: str,
    ) -> Result[ArangoCollection]:
        """
        Read a collection info from arangodb.

        Notes
        -----
        The result is an object describing the collection with the following attributes:
            - **id**: The identifier of the collection.
            - **name**: The name of the collection.
            - **status**: The status of the collection as number (`Every other status indicates a corrupted collection`).
                - 3: loaded
                - 5: deleted
            - **type**: The type of the collection as number.
                - 2: document collection (normal case)
                - 3: edge collection
            - **isSystem**: If true then the collection is a system collection.


        **Warnings**: Accessing collections by their numeric ID is deprecated from version 3.4.0 on.
        You should reference them via their names instead.


        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            A `ArangoCollection` object is returned. (minimum version)

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
            method_type=MethodType.GET,
            endpoint=f"/_api/collection/{name}",
            read=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
