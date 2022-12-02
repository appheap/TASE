from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response, ArangoCollection
from aioarango.typings import Result


class TruncateCollection(Endpoint):
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def truncate_collection(
        self,
        name: str,
        wait_for_sync: Optional[bool] = False,
        compact: Optional[bool] = True,
    ) -> Result[ArangoCollection]:
        """
        Remove all documents from the collection, but leave the indexes intact.

        Notes
        -----
        **Warning**:
        Accessing collections by their numeric ID is deprecated from version 3.4.0 on.
        You should reference them via their names instead.



        Parameters
        ----------
        name : str
            Name of the collection to truncate.
        wait_for_sync : bool, default : False
            If true then the data is synchronized to disk before returning from the truncate operation (default: false)
        compact : bool, default : True
            If `true` (default) then the storage engine is told to start a compaction
            in order to free up disk space. This can be resource intensive. If the only
            intention is to start over with an empty collection, specify `false`.

        Returns
        -------
        Result
            An `ArangoCollection` object is returned. (with minimum info about the collection)

        Raises
        ------
        ValueError
            If collection name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/truncate",
            params={
                "waitForSync": wait_for_sync,
                "compact": compact,
            },
            write=name,
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
