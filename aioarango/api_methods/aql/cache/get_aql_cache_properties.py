from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, AQLCacheProperties
from aioarango.typings import Result
from aioarango.utils.aql_utils import format_aql_cache


class GetAQLCacheProperties(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # Is returned if the properties can be retrieved successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request.
    )

    async def get_aql_cache_properties(
        self,
    ) -> Result[AQLCacheProperties]:
        """
        Return the global AQL query results cache configuration.

        Notes
        -----
        The configuration is a JSON object with the following properties:
            - **mode**: the mode the AQL query results cache operates in. The mode is one of the following
              values: `off`, `on` or `demand`.

            - **maxResults**: the maximum number of query results that will be stored per database-specific cache.

            - **maxResultsSize**: the maximum cumulated size of query results that will be stored per
              database-specific cache.

            - **maxEntrySize**: the maximum individual result size of queries that will be stored per
              database-specific cache.

            - **includeSystem**: whether or not results of queries that involve system collections will be stored in the query results cache.


        Returns
        -------
        AQLCacheProperties
            An `AQLCacheProperties` object is returned on success.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/query-cache/properties",
        )

        def response_handler(resp: Response) -> AQLCacheProperties:
            if not resp.is_success:
                raise ArangoServerError(resp, request)

            # status_code 200
            return AQLCacheProperties.parse_obj(format_aql_cache(resp.body))

        return await self.execute(request, response_handler)
