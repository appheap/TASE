from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Response, Request
from aioarango.typings import Result


class ClearAQLCacheEntries(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # The server will respond with HTTP 200 when the cache was cleared successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request.
    )

    async def clear_aql_cache_entries(self) -> Result[bool]:
        """
        Clear the query results cache for the current database.


        Returns
        -------
        Result
            `True` if the query cache was cleared successfully.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        request = Request(
            method_type=MethodType.DELETE,
            endpoint="/_api/query-cache",
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return True

        return await self.execute(request, response_handler)
