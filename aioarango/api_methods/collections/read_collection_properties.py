from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class ReadCollectionProperties:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def read_collection_properties(
        self: Endpoint,
        name: str,
    ) -> Result[ArangoCollection]:
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/collection/{name}/properties",
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
