from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, AQLTrackingData
from aioarango.typings import Result
from aioarango.utils.aql_utils import format_aql_tracking


class GetAQLQueryTrackingProperties(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # Is returned if properties were retrieved successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
    )

    async def get_aql_query_tracking_properties(self) -> Result[AQLTrackingData]:
        """
        Return the current query tracking configuration

        Returns
        -------
        AQLTrackingData
            An `AQLTrackingData` object is returned on success.


        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/query/properties",
        )

        def response_handler(resp: Response) -> AQLTrackingData:
            if not resp.is_success:
                raise ArangoServerError(resp, request)

            # status_code 200
            return AQLTrackingData.parse_obj(format_aql_tracking(resp.body))

        return await self.execute(request, response_handler)
