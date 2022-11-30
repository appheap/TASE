from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response, DatabaseInfo
from aioarango.typings import Result


class GetDatabaseInfo(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # is returned if the information was retrieved successfully.
        400,
        # is returned if the request is invalid.
        404,
        # is returned if the database could not be found.
    )

    async def get_database_info(
        self,
    ) -> Result[DatabaseInfo]:
        """
        Retrieve the properties of the current database.

        Returns
        -------
        Result
            Database info if retrieval was successful.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If retrieval fails.

        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/database/current",
        )

        def response_handler(response: Response) -> DatabaseInfo:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return DatabaseInfo.parse_obj(response.body["result"])

        return await self.execute(request, response_handler)
