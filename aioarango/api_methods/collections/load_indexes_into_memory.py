from aioarango.api import Endpoint
from aioarango.enums import MethodType
from aioarango.errors import ArangoServerError, ErrorType
from aioarango.models import Request, Response
from aioarango.typings import Result


class LoadIndexesIntoMemory:
    error_codes = (ErrorType.ARANGO_DATA_SOURCE_NOT_FOUND,)
    status_codes = (
        200,
        # If the indexes have all been loaded
        400,
        # If the collection-name is missing, then a HTTP 400 is returned.
        404,  # 1203
        # If the collection-name is unknown, then a HTTP 404 is returned.
    )

    async def load_indexes_into_memory(
        self: Endpoint,
        name: str,
    ) -> Result[bool]:
        """
        Load collection indexes into memory.

        Notes
        -----
        - This route tries to cache all index entries
          of this collection into the main memory.
          Therefore, it iterates over all indexes of the collection
          and stores the indexed values, not the entire document data,
          in memory.

        - All lookups that could be found in the cache are much faster
          than lookups not stored in the cache so you get a nice performance boost.
          It is also guaranteed that the cache is consistent with the stored data

        - This function honors all memory limits, if the indexes you want
          to load are smaller than your memory limit this function guarantees that most
          index values are cached.

        - If the index is larger than your memory limit this function will fill up values
          up to this limit and for the time being there is no way to control which indexes
          of the collection should have priority over others.

        - On success this function returns an object with attribute **result** set to `true`.

        - **Warning**: Accessing collections by their numeric ID is deprecated from version 3.4.0 on. You should reference them via their names instead.



        Parameters
        ----------
        name : str
            Name of the collection.

        Returns
        -------
        Result
            `True` if the operation was successful.


        Raises
        ------
        ValueError
            If name is invalid.
        aioarango.errors.ArangoServerError
            If operation fails.
        """
        if name is None or not len(name):
            raise ValueError(f"`name` has invalid value: `{name}`")

        request = Request(
            method_type=MethodType.PUT,
            endpoint=f"/_api/collection/{name}/loadIndexesIntoMemory",
            read=name,
        )

        def response_handler(response: Response) -> bool:
            if not response.is_success:
                raise ArangoServerError(response, request)

            # status_code 200
            return response.body["result"]

        return await self.execute(request, response_handler)
