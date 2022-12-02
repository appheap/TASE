from typing import List, Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, AQLQuery
from aioarango.typings import Result
from aioarango.utils.aql_utils import format_aql_query


class GetRunningAQLQueries(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # Is returned when the list of queries can be retrieved successfully.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
        403,
        # HTTP 403 is returned in case the all parameter was used, but the request
        # was made in a different database than _system, or by a non-privileged user.
    )

    async def get_running_aql_queries(
        self,
        get_from_all_databases: Optional[bool] = None,
    ) -> Result[List[AQLQuery]]:
        """
        Return an array containing the AQL queries currently running in the selected database

        Notes
        -----
        Each query is a JSON object with the following attributes:
            - **id**: the query's id.
            - **database**: the name of the database the query runs in.
            - **user**: the name of the user that started the query.
            - **query**: the query string (potentially truncated).
            - **bindVars**: the bind parameter values used by the query.
            - **started**: the date and time when the query was started.
            - **runTime**: the query's total run time.
            - **stream**: whether the query uses a streaming cursor or not.
            - **state**: the query's current execution state (as a string). One of:

                - "initializing"
                - "parsing"
                - "optimizing ast"
                - "loading collections"
                - "instantiating plan"
                - "optimizing plan"
                - "executing"
                - "finalizing"
                - "finished"
                - "killed"
                - "invalid"




        Parameters
        ----------
        get_from_all_databases : bool, optional
            If set to `true`, will return the currently running queries in all databases, not just the selected one.
            Using the parameter is only allowed in the `system` database and with `superuser` privileges.

        Returns
        -------
        Result
            List of current running AQL queries.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/query/current",
            params={
                "all": get_from_all_databases,
            }
            if get_from_all_databases is not None
            else None,
        )

        def response_handler(response: Response) -> List[AQLQuery]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return [AQLQuery.parse_obj(format_aql_query(q)) for q in response.body]

        return await self.execute(request, response_handler)
