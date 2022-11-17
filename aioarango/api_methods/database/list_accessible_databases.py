from typing import List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Result


class ListAccessibleDatabases:
    error_codes = ()
    status_codes = (
        200,
        # is returned if the list of database was compiled successfully.
        400,
        # is returned if the request is invalid.
    )

    async def list_accessible_databases(self: Endpoint) -> Result[List[str]]:
        """
        Retrieve the list of all databases the current user can access without
        specifying a different username or password.

        Returns
        -------
        Result
            List of accessible databases if successful.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/database/user",
        )

        def response_handler(response: Response) -> List[str]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body["result"]

        return await self.execute(request, response_handler)
