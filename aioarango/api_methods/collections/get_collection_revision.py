from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class GetCollectionRevision:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        # Returns information about the collection:
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def get_collection_revision(
        self: Endpoint,
        name: str,
    ) -> Result[ArangoCollection]:
        """
        Get collection revision ID. In addition, the result will also contain the
        collection's revision id. The revision id is a server-generated
        string that clients can use to check whether data in a collection
        has changed since the last revision check.

        - **revision**: The collection revision id as a string.


        Notes
        -----
        - **Warning**: Accessing collections by their numeric ID is deprecated from version 3.4.0 on. You should reference them via their names instead.


        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            An `ArangoCollection` object. (full version with `revision` attributes set)

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
            endpoint=f"/_api/collection/{name}/revision",
            read=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
