from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result


class DropDatabase:
    error_codes = (
        ErrorType.HTTP_BAD_PARAMETER,
        ErrorType.ARANGO_DATABASE_NOT_FOUND,
    )
    status_codes = (
        200,
        # is returned if the database was dropped successfully.
        400,  # 400
        # is returned if the request is malformed.
        403,
        # is returned if the request was not executed in the _system database.
        404,  # 1228
        # is returned if the database could not be found.
    )

    async def drop_database(
        self: Endpoint,
        name: str,
    ) -> Result[bool]:
        """
        Drop the database along with all data stored in it.

        Notes
        -----
        dropping a database is only possible from within the **_system** database.
        The **_system** database itself cannot be dropped.


        Parameters
        ----------
        name : str
            Database name.

        Returns
        -------
        Result
            True if database was deleted successfully.
        """
        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/database/{name}",
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return True

        return await self.execute(request, response_handler)
