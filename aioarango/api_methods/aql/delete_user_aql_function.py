from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result


class DeleteUserAQLFunction(Endpoint):
    error_codes = (ErrorType.QUERY_FUNCTION_NOT_FOUND,)
    status_codes = (
        200,
        # If the function can be removed by the server, the server will respond with HTTP 200.
        400,
        # If the user function name is malformed, the server will respond with HTTP 400.
        404,  # 1582
        # If the specified user function does not exist, the server will respond with HTTP 404.
    )

    async def delete_user_aql_function(
        self,
        name: str,
        group: Optional[bool] = None,
    ) -> Result[int]:
        """
        Remove an existing AQL user function or function group, identified by **name**.


        Notes
        -----
        If the function can be removed by the server, the server will respond with HTTP 200;

            - **error**: boolean flag to indicate whether an error occurred (false in this case).
            - **code**: the HTTP status code.
            - **deletedCount**: The number of deleted user functions, always `1` when group is set to `false`.
              Any number `>= 0` when group is set to `true`.


        Parameters
        ----------
        name : str
            Name of the function to remove.
        group : bool, optional
            If set to `True`, the function name provided in name is treated as
            a namespace prefix, and all functions in the specified namespace will be deleted.
            The returned number of deleted functions may become 0 if none matches the string.
            If set to `False`, the function name provided in name must be fully
            qualified, including any namespaces. If none matches the name, HTTP 404 is returned.

        Returns
        -------
        Result
            Number of AQL functions deleted if operation was successful.

        Raises
        ------
        ValueError
            If `name` has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if not name:
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/aqlfunction/{name}",
            params={"group": group} if group is not None else None,
        )

        def response_handler(response: Response) -> int:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body["deletedCount"]

        return await self.execute(request, response_handler)
