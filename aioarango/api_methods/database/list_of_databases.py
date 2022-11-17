from typing import List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result


class ListOfDatabases:
    error_codes = (ErrorType.ARANGO_USE_SYSTEM_DATABASE,)
    status_codes = (
        200,
        # is returned if the list of database was compiled successfully.
        400,
        # is returned if the request is invalid.
        403,  # 1230
        # is returned if the request was not executed in the _system database.
    )

    async def list_of_databases(
        self: Endpoint,
    ) -> Result[List[str]]:
        """
        Retrieves the list of all existing databases.

        Notes
        -----
        - retrieving the list of databases is only possible from within the **_system** database.

        - You should use the GET user API to fetch the list of the available databases now.

        Returns
        -------
        Result
            Database names.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/database",
        )

        def response_handler(response: Response) -> List[str]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            return response.body["result"]

        return await self.execute(request, response_handler)
