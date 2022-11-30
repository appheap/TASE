from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType, AQLCacheMode
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, AQLCacheProperties
from aioarango.typings import Result, Json
from aioarango.utils.aql_utils import format_aql_cache


class ChangeAQLCacheProperties(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # Is returned if the properties can be retrieved successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request.
    )

    async def change_aql_cache_properties(
        self,
        mode: Optional[AQLCacheMode] = None,
        max_results: Optional[int] = None,
        max_results_size: Optional[int] = None,
        max_entry_size: Optional[int] = None,
        include_system: Optional[bool] = None,
    ) -> Result[AQLCacheProperties]:
        """
        Globally adjust the AQL query results cache properties

        Notes
        -----
        **Note**: changing the properties may invalidate all results in the cache.
        The global properties for AQL query cache.

        The properties need to be passed in the attribute properties in the body
        of the HTTP request. properties object needs to be a JSON object with the following
        properties:

        A JSON object with these properties is required:
            - **mode**: the mode the AQL query results cache operates in. The mode is one of the following
              values: `off`, `on` or `demand`.

            - **maxResults**: the maximum number of query results that will be stored per database-specific cache.

            - **maxResultsSize**: the maximum cumulated size of query results that will be stored per
              database-specific cache.

            - **maxEntrySize**: the maximum individual result size of queries that will be stored per
              database-specific cache.

            - **includeSystem**: whether or not results of queries that involve system collections will be stored in the query results cache.

        Parameters
        ----------
        mode : AQLCacheMode, optional
            Operation mode. Allowed values are "off", "on" and "demand".
        max_results : int, optional
            Max number of query results stored per database-specific cache.
        max_results_size : int, optional
            Max cumulative size of query results stored per database-specific cache.
        max_entry_size : int, optional
            Max entry size of each query result stored per database-specific cache.
        include_system : bool, optional
            Store results of queries in system collections.

        Returns
        -------
        AQLCacheProperties
            An `AQLCacheProperties` object is returned on success.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """

        data: Json = {}
        if mode is not None:
            data["mode"] = mode.value
        if max_results is not None:
            data["maxResults"] = max_results
        if max_results_size is not None:
            data["maxResultsSize"] = max_results_size
        if max_entry_size is not None:
            data["maxEntrySize"] = max_entry_size
        if include_system is not None:
            data["includeSystem"] = include_system

        request = Request(
            method_type=MethodType.PUT,
            endpoint="/_api/query-cache/properties",
            data=data,
        )

        def response_handler(resp: Response) -> AQLCacheProperties:
            if not resp.is_success:
                raise ArangoServerError(resp, request)

            # status_code 200
            return AQLCacheProperties.parse_obj(format_aql_cache(resp.body))

        return await self.execute(request, response_handler)
