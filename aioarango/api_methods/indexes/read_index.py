from typing import Union

from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.models.index import (
    BaseArangoIndex,
    EdgeIndex,
    FullTextIndex,
    GeoIndex,
    HashIndex,
    InvertedIndex,
    PersistentIndex,
    PrimaryIndex,
    SkipListIndex,
    TTLIndex,
    MultiDimensionalIndex,
)
from aioarango.typings import Result


class ReadIndex:
    error_codes = (
        ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,
        ErrorType.ARANGO_INDEX_NOT_FOUND,
    )
    status_codes = (
        200,
        # If the index exists, then a HTTP 200 is returned.
        404,  # 1203, 1212
        # If the index does not exist, then a HTTP 404 is returned.
    )

    async def read_index(
        self: Endpoint,
        index_id: str,
    ) -> Result[
        Union[EdgeIndex, FullTextIndex, GeoIndex, HashIndex, InvertedIndex, PersistentIndex, PrimaryIndex, SkipListIndex, TTLIndex, MultiDimensionalIndex]
    ]:
        """
        Read an Index info.

        Notes
        -----
        The result is an object describing the index. It has at least the following attributes:
            - **id**: the identifier of the index
            - **type**: the index typeq
        All other attributes are type-dependent. For example, some indexes provide
        `unique` or `sparse` flags, whereas others don't. Some indexes also provide
        a selectivity estimate in the `selectivityEstimate` attribute of the result.

        Parameters
        ----------
        index_id : str
            ID of the index to read.

        Returns
        -------
        Result
            A subclass of `BaseArangoIndex` describing the index object.

        Raises
        ------
        ValueError
            If `index_id` is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.

        """
        if index_id is None or not len(index_id):
            raise ValueError(f"`index_id` has invalid value: `{index_id}`")

        request = Request(
            method_type=MethodType.GET,
            endpoint=f"/_api/index/{index_id}",
        )

        def response_handler(
            response: Response,
        ) -> Union[EdgeIndex, FullTextIndex, GeoIndex, HashIndex, InvertedIndex, PersistentIndex, PrimaryIndex, SkipListIndex, TTLIndex, MultiDimensionalIndex]:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return BaseArangoIndex.from_db(response.body)

        return await self.execute(request, response_handler)
