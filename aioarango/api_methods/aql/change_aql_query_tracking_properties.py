from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, AQLTrackingData
from aioarango.typings import Result, Json
from aioarango.utils.aql_utils import format_aql_tracking


class ChangeAQLQueryTrackingProperties(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # Is returned if properties were retrieved successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
    )

    async def change_aql_query_tracking_properties(
        self,
        enabled: Optional[bool] = None,
        max_slow_queries: Optional[int] = None,
        slow_query_threshold: Optional[int] = None,
        max_query_string_length: Optional[int] = None,
        track_bind_vars: Optional[bool] = None,
        track_slow_queries: Optional[bool] = None,
    ) -> Result[AQLTrackingData]:
        """
        Change the properties for the AQL query tracking

        Notes
        -----
        A JSON object with these properties is required:
            - **enabled**: If set to true, then queries will be tracked. If set to
              false, neither queries nor slow queries will be tracked.

            - **trackSlowQueries**: If set to true, then slow queries will be tracked
              in the list of slow queries if their runtime exceeds the value set in

            - **slowQueryThreshold**. In order for slow queries to be tracked, the enabled
              property must also be set to true.

            - **trackBindVars**: If set to `true`, then the bind variables used in queries will be tracked
              along with queries.

            - **maxSlowQueries**: The maximum number of slow queries to keep in the list
              of slow queries. If the list of slow queries is full, the oldest entry in
              it will be discarded when additional slow queries occur.

            - **slowQueryThreshold**: The threshold value for treating a query as slow. A
              query with a runtime greater or equal to this threshold value will be
              put into the list of slow queries when slow query tracking is enabled.
              The value for slowQueryThreshold is specified in seconds.

            - **maxQueryStringLength**: The maximum query string length to keep in the list of queries.
              Query strings can have arbitrary lengths, and this property
              can be used to save memory in case very long query strings are used. The
              value is specified in bytes.

        The properties need to be passed in the attribute properties in the body
        of the HTTP request. properties object needs to be a JSON object.

        After the properties have been changed, the current set of properties will
        be returned in the HTTP response.

        Parameters
        ----------
        enabled : bool, optional
            Track queries if set to True.
        max_slow_queries : int, optional
            Max number of slow queries to track. Oldest entries are discarded first.
        slow_query_threshold : int, optional
            Runtime threshold (in seconds) for treating a query as slow.
        max_query_string_length : int, optional
            Max query string length (in bytes) tracked.
        track_bind_vars : bool, optional
            If set to `True`, track bind variables used in queries.
        track_slow_queries : bool, optional
            If set to `True`, track slow queries whose runtimes
            exceed **slow_query_threshold**. To use this, parameter **enabled** must
            be set to `True`.

        Returns
        -------
        AQLTrackingData
            An `AQLTrackingData` object is returned on success.


        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        data: Json = {}
        if enabled is not None:
            data["enabled"] = enabled
        if max_slow_queries is not None:
            data["maxSlowQueries"] = max_slow_queries
        if max_query_string_length is not None:
            data["maxQueryStringLength"] = max_query_string_length
        if slow_query_threshold is not None:
            data["slowQueryThreshold"] = slow_query_threshold
        if track_bind_vars is not None:
            data["trackBindVars"] = track_bind_vars
        if track_slow_queries is not None:
            data["trackSlowQueries"] = track_slow_queries

        request = Request(
            method_type=MethodType.PUT,
            endpoint="/_api/query/properties",
            data=data,
        )

        def response_handler(resp: Response) -> AQLTrackingData:
            if not resp.is_success:
                raise ArangoServerError(resp, request)

            # status_code 200
            return AQLTrackingData.parse_obj(format_aql_tracking(resp.body))

        return await self.execute(request, response_handler)
