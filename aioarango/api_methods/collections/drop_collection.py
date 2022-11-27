from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result, Params


class DropCollection:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def drop_collection(
        self: Endpoint,
        name: str,
        is_system_collection: Optional[bool] = None,
    ) -> Result[bool]:
        """
        Drop a collection identified by collection-name.

        Notes
        -----
        If the collection was successfully dropped, an object is returned with
        the following attributes:
            - `error`: false
            - `id`: The identifier of the dropped collection.


        **Warnings**:
        Accessing collections by their numeric `ID` is deprecated from version 3.4.0 on.
        You should reference them via their `names` instead.


        Parameters
        ----------
        name : str
            Name of the collection to drop.
        is_system_collection : bool, optional
            Whether the collection to drop is a system collection or not. This parameter
            must be set to `True` in order to drop a system collection.

        Returns
        -------
        Result
            `True` if the collection dropped successfully.

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        params: Params = {}
        if is_system_collection is not None:
            params["isSystem"] = is_system_collection

        request = Request(
            method_type=MethodType.DELETE,
            endpoint=f"/_api/collection/{name}",
            params=params,
            write=name,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return True

        return await self.execute(request, response_handler)
