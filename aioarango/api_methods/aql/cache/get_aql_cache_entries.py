from typing import List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, AQLQueryCacheEntry
from aioarango.typings import Result
from aioarango.utils.aql_utils import format_query_cache_entry


class GetAQLCacheEntries(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # Is returned when the list of results can be retrieved successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
    )

    async def get_aql_cache_entries(self) -> Result[List[AQLQueryCacheEntry]]:
        """
        Return an array containing the AQL query results currently stored in the query results cache of the selected database.

        Each result is a JSON object with the following attributes:
            - **hash**: the query result's hash.

            - **query**: the query string.

            - **bindVars**: the query's bind parameters. this attribute is only shown if tracking for
              bind variables was enabled at server start.

            - **size**: the size of the query result and bind parameters, in bytes

            - **results**: number of documents/rows in the query result.

            - **started**: the date and time when the query was stored in the cache.

            - **hits**: number of times the result was served from the cache (can be
              `0` for queries that were only stored in the cache but were never accessed
              again afterwards).

            - **runTime**: the query's run time.

            - **dataSources**: an array of collections/Views the query was using.


        Returns
        -------
        Result
            List of `AQLQueryCacheEntry` objects.


        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/query-cache/entries",
        )

        def response_handler(response: Response) -> List[AQLQueryCacheEntry]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return [AQLQueryCacheEntry.parse_obj(format_query_cache_entry(entry)) for entry in response.body]

        return await self.execute(request, response_handler)
