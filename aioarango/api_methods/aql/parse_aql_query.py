from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Response, Request
from aioarango.typings import Result, Json
from aioarango.utils.generic import format_body


class ParseAQlQuery(Endpoint):
    error_codes = ()
    status_codes = (
        200,
        # If the query is valid, the server will respond with HTTP 200 and
        # return the names of the bind parameters it found in the query (if any) in
        # the `bindVars` attribute of the response. It will also return an array
        # of the collections used in the query in the `collections` attribute.
        # If a query can be parsed successfully, the `ast` attribute of the returned
        # JSON will contain the abstract syntax tree representation of the query.
        # The format of the `ast` is subject to change in future versions of
        # ArangoDB, but it can be used to inspect how ArangoDB interprets a given
        # query. Note that the abstract syntax tree will be returned without any
        # optimizations applied to it.
        400,
        # The server will respond with HTTP 400 in case of a malformed request,
        # or if the query contains a parse error. The body of the response will
        # contain the error details embedded in a JSON object.
    )

    async def parse_aql_query(
        self,
        query: str,
    ) -> Result[Json]:
        """
        Parse an AQL query.

        Notes
        -----
        This endpoint is for query validation only. To actually query the database, see `/api/cursor.`


        Parameters
        ----------
        query : str
            Query to validate.


        Returns
        -------
        Json
            Query details.

        Raises
        ------
        ValueError
            If query has invalid value.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if not query:
            raise ValueError(f"`query` has invalid value: `{query}`")

        request = Request(
            method_type=MethodType.POST,
            endpoint="/_api/query",
            data={
                "query": query,
            },
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            body = format_body(response.body)
            if "bindVars" in body:
                body["bind_vars"] = body.pop("bindVars")
            return body

        return await self.execute(request, response_handler)
