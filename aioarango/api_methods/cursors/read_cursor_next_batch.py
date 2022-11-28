from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Json


class ReadCursorNextBatch(Endpoint):
    error_codes = (ErrorType.CURSOR_NOT_FOUND,)
    status_codes = (
        200,
        # The server will respond with HTTP 200 in case of success.
        400,
        # If the cursor identifier is omitted, the server will respond with HTTP 404. # todo: is the 404 code correct here?
        404,  # 1600
        # If no cursor with the specified identifier can be found, the server will respond with HTTP 404.
        410,
        # The server will respond with HTTP 410 if a server which processes the query
        # or is the leader for a shard which is used in the query stops responding, but
        # the connection has not been closed.
        503,
        # The server will respond with HTTP 503 if a server which processes the query
        # or is the leader for a shard which is used in the query is down, either for
        # going through a restart, a failure or connectivity issues.
    )

    async def read_cursor_next_batch(
        self,
        cursor_id: str,
        cursor_type: Optional[str] = "cursor",
    ) -> Result[Json]:
        """
        Read next batch from a cursor.

        Notes
        -----
        If the cursor is still alive, returns an object with the following attributes:
            - **id**: a cursor-identifier.
            - **result**: a list of documents for the current batch.
            - **hasMore**: `false` if this was the last batch.
            - **count**: if present the total number of elements.
            - **code**: an HTTP status code.
            - **error**: a `boolean` flag to indicate whether an error occurred.
            - **errorNum**: a server error number (if error is `true`).
            - **errorMessage**: a descriptive error message (if error is `true`).
            - **extra**: an object with additional information about the query result, with
              the nested objects stats and warnings. Only delivered as part of the last
              batch in case of a cursor with the stream option enabled.

        Note that even if **hasMore** returns `true`, the next call might
        still return no documents. If, however, **hasMore** is `false`, then
        the cursor is exhausted. Once the **hasMore** attribute has a value of
        `false`, the client can stop.


        Parameters
        ----------
        cursor_id : str
            ID of the cursor.
        cursor_type : str, default : "cursor"
            Type of the cursor. (default is "cursor")

        Returns
        -------
        Result
            A `Json` object is returned on success.

        Raises
        ------
        ValueError
            If the `cursor_id` or `cursor_type` have invalid values.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if cursor_id is None or not len(cursor_id):
            raise ValueError(f"`cursor_id` has invalid value: `{cursor_id}`")

        if cursor_type is None or not len(cursor_type):
            raise ValueError(f"`cursor_type` has invalid value: `{cursor_type}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/{cursor_type}/{cursor_id}",
        )

        def response_handler(response: Response) -> Json:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body

        return await self.execute(request, response_handler)
