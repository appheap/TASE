from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Result


class CreateUserAQLFunction(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # If the function already existed and was replaced by the
        # call, the server will respond with HTTP 200.
        201,
        # If the function can be registered by the server, the server will respond with
        # HTTP 201.
        400,
        # If the JSON representation is malformed or mandatory data is missing from the
        # request, the server will respond with HTTP 400.
    )

    async def create_user_aql_function(
        self,
        name: str,
        code: str,
        is_deterministic: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Create User AQL function.

        Parameters
        ----------
        name : str
            Name of the AQL function.
        code : str
            Function definition in Javascript.
        is_deterministic : bool, optional
            An optional `boolean` value to indicate whether the function
            results are fully deterministic (function return value solely depends on
            the input value and return value is the same for repeated calls with same
            input). The isDeterministic attribute is currently not used but may be
            used later for optimizations.

        Returns
        -------
        Result
           Whether the function `was` created or replaced an existing one.

        Raises
        ------
        ValueError
            If `name` or `code` parameters have invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if not name:
            raise ValueError(f"`name` has invalid value: `{name}`")

        if not code:
            raise ValueError(f"`code` has invalid value: `{code}`")

        data = {
            "name": name,
            "code": code,
        }

        if is_deterministic is not None:
            data["isDeterministic"] = is_deterministic

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/aqlfunction",
            data=data,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200, 201
            return response.body["isNewlyCreated"]

        return await self.execute(request, response_handler)
