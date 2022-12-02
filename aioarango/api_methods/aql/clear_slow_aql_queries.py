from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Result


class ClearSlowAQLQueries(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # The server will respond with HTTP 200 when the list of queries was cleared successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
        403,
        # HTTP 403 is returned in case the all parameter was used, but the request
        # was made in a different database than _system, or by an non-privileged user.
    )

    async def clear_slow_aql_queries(
        self,
        clear_from_all_databases: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Clear the list of slow AQL queries in the currently selected database

        Parameters
        ----------
        clear_from_all_databases : bool, optional
            If set to `true`, will clear the slow query history in all databases, not just the selected one.
            Using the parameter is only allowed in the `system` database and with `superuser` privileges.

        Returns
        -------
        Result
            True if the operations was successful.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        request = Request(
            method_type=MethodType.DELETE,
            endpoint="/_api/query/slow",
            params={
                "all": clear_from_all_databases,
            }
            if clear_from_all_databases is not None
            else None,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return True

        return await self.execute(request, response_handler)
