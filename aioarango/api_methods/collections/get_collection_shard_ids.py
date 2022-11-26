from typing import Optional

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import ArangoCollection, Request, Response
from aioarango.typings import Result


class GetCollectionShardIDs:
    error_codes = (
        ErrorType.NOT_IMPLEMENTED,
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
    )
    status_codes = (
        200,
        # Returns the collection's shards.
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then an HTTP 404 is returned.
        501,  # 9
        # HTTP 501 is returned if the method is called on a single server.
    )

    async def get_collection_shard_ids(
        self: Endpoint,
        name: str,
        show_details: Optional[bool] = False,
    ) -> Result[ArangoCollection]:
        """
        Get Shard IDs of a collection.

        Notes
        -----
        - **Important**: This method is only available in a `cluster Coordinator`.

        Parameters
        ----------
        name : str
            Name of the collection
        show_details : bool, default : False
            If set to `true`, it will return a JSON object with the
            shard IDs as object attribute keys, and the responsible servers for each shard mapped to them.
            In the detailed response, the leader shards will be first in the arrays.

        Returns
        -------
        Result
            An `ArangoCollection` object.

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
            method_type=MethodType.GET,
            endpoint=f"/_api/collection/{name}/shards",
            params={
                "details": show_details,
            },
        )

        def response_handler(response: Response) -> ArangoCollection:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return ArangoCollection.parse_from_dict(response.body)

        return await self.execute(request, response_handler)
