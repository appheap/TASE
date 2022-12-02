from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Response, Request
from aioarango.typings import Result


class KillRunningAQLQuery(Endpoint):
    error_codes = (ErrorType.QUERY_NOT_FOUND,)
    status_codes = (
        200,
        # The server will respond with HTTP 200 when the query was still running when
        # the kill request was executed and the query's kill flag was set.
        400,
        # The server will respond with HTTP 400 in case of a malformed request.
        403,
        # HTTP 403 is returned in case the all parameter was used, but the request
        # was made in a different database than `_system`, or by a `non-privileged user`.
        404,  # 1591
        # The server will respond with HTTP 404 when no query with the specified `id` was found.
    )

    async def kill_running_aql_query(
        self,
        query_id: str,
        kill_in_all_databases: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Kill a running query in the currently selected database. The query will be
        terminated at the next cancellation point.


        Parameters
        ----------
        query_id : str
            ID of the query to kill.
        kill_in_all_databases : bool, optional
            If set to `true`, will attempt to kill the specified query in all databases, not just the selected one.
            Using the parameter is only allowed in the `system` database and with `superuser` privileges.


        Returns
        -------
        bool
            True if the kill request was sent successfully.

        Raises
        ------
        ValueError
            If `query_id` has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if not query_id:
            raise ValueError(f"`query` has invalid value: `{query_id}`")

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/query/{query_id}",
            params={"all": kill_in_all_databases} if kill_in_all_databases is not None else None,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return True

        return await self.execute(request, response_handler)
