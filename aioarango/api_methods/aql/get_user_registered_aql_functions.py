from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Result, Jsons


class GetUserRegisteredAQLFunctions(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # on success HTTP 200 is returned.
        400,
        # If the user function name is malformed, the server will respond with HTTP 400.
    )

    async def get_user_registered_aql_functions(
        self,
        namespace: Optional[str] = None,
    ) -> Result[Jsons]:
        """
        Return all registered AQL user functions.

        # todo: result parsing of this endpoint should be investigated in more detail.


        Notes
        -----
        - On success, a json document with these Properties is returned:

            - **error**: boolean flag to indicate whether an error occurred (false `in` this case).
            - **code**: the HTTP status code.
            - **result**: All functions, or the ones matching the namespace parameter

                - **name**: The fully qualified name of the user function
                - **code**: A string representation of the function body
                - **isDeterministic**: an optional `boolean` value to indicate whether the function
                  results are fully deterministic (function return value solely depends on
                  the input value and return value is the same for repeated calls with same
                  input). The isDeterministic attribute is currently not used but may be
                  used later for optimizations.


        - If the user function name is malformed, the server will respond with HTTP 400 and a json document with these Properties is returned:

            - **error**: `boolean` flag to indicate whether an error occurred (`true` in this case).
            - **code**: the HTTP status code.
            - **errorNum**: the server error number.
            - **errorMessage**: a descriptive error message



        Parameters
        ----------
        namespace : str, optional
            Returns all registered AQL user functions from namespace `namespace` under `result`.


        Returns
        -------
        Result
            All registered AQL user functions.

        Raises
        ------
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        request = Request(
            method_type=MethodType.GET,
            endpoint="/_api/aqlfunction",
            params={
                "namespace": namespace,
            }
            if namespace is not None
            else None,
        )

        def response_handler(response: Response) -> Jsons:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            functions: Jsons = response.body["result"]
            for function in functions:
                if "isDeterministic" in function:
                    function["is_deterministic"] = function.pop("isDeterministic")

            return functions

        return await self.execute(request, response_handler)
