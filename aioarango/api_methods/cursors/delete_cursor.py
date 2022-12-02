from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError
from aioarango.models import Request, Response
from aioarango.typings import Result


class DeleteCursor(Endpoint):
    error_codes = ()
    status_codes = (
        202,
        # is returned if the server is aware of the cursor.
        404,
        # is returned if the server is not aware of the cursor. It is also
        # returned if a cursor is used after it has been destroyed.
    )

    async def delete_cursor(
        self,
        cursor_id: str,
        cursor_type: Optional[str] = "cursor",
    ) -> Result[bool]:
        """
        Delete the cursor and frees the resources associated with it.

        Notes
        -----
        - The cursor will automatically be destroyed on the server when the client has
          retrieved all documents from it. The client can also explicitly destroy the
          cursor at any earlier time using an HTTP DELETE request. The cursor id must
          be included as part of the URL.

        - Note: the server will also destroy abandoned cursors automatically after a
          certain server-controlled timeout to avoid resource leakage.


        Parameters
        ----------
        cursor_id : str
            ID of the cursor.
        cursor_type : str, default : "cursor"
            Type of the cursor. (default is "cursor")

        Returns
        -------
        Result
            `True` if the deletion was successful.

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
            method_type=MethodType.DELETE,
            endpoint=f"/_api/{cursor_type}/{cursor_id}",
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 202
            return True

        return await self.execute(request, response_handler)
