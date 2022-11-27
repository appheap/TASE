from typing import Optional, List

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.models.index import BaseArangoIndex
from aioarango.typings import Result


class ReadAllCollectionIndexes:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        # returns a JSON object containing a list of indexes on that collection.
        404,  # 1203
    )

    async def read_all_collection_indexes(
        self: Endpoint,
        name: str,
        with_stats: Optional[bool] = False,
        with_hidden: Optional[bool] = False,
    ) -> Result[List[BaseArangoIndex]]:
        """
        Get all indexes of a collection.

        Notes
        -----
        Returns an object with an attribute **indexes** containing an array of all
        index descriptions for the given collection. The same information is also
        available in the **identifiers** as an object with the index handles as
        keys.

        Parameters
        ----------
        name : str
            Name of the collection.
        with_stats : bool, default : False
            Whether to include figures and estimates in the result or not.
        with_hidden : bool, default : False
            Whether to include hidden indexes in the result or not.

        Returns
        -------
        Result
            List of all indexed of the collection.

        Raises
        ------
        ValueError
            If name is invalid or the `type` of an index in invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/index",
            params={
                "collection": name,
                "withStats": with_stats,
                "withHidden": with_hidden,
            },
        )

        def response_handler(response: Response) -> List[BaseArangoIndex]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            # todo: `identifiers` attribute in the response body contains the same indexes only it is a dictionary which its keys are index IDs.
            return [BaseArangoIndex.from_db(item) for item in response.body["indexes"]]

        return await self.execute(request, response_handler)
